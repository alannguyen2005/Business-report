"""
compute_metrics.py
------------------
Tính toàn bộ con số cho một kỳ phân tích. Deterministic — chạy lại cho ra
kết quả y hệt, không phụ thuộc LLM.

Phân công:
  script này  → con số (descriptive, diagnostic, forecast)
  agent       → diễn giải, narrative, khuyến nghị chiến lược

Đọc  : config.yaml → data.file, schema, analysis, forecast
Ghi  : data/pipeline/{stem}/profile.json
       data/pipeline/{stem}/descriptive_output.json
       data/pipeline/{stem}/diagnostic_output.json
       data/pipeline/{stem}/predictive_output.json

Dùng : python compute_metrics.py
"""

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy import stats

# Thư viện dự báo nặng — import có bảo vệ để pipeline vẫn chạy khi máy thiếu.
# Windows ARM64 không có wheel cho statsmodels; Ubuntu trên GitHub Actions thì có.
try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
except ImportError:                                    # pragma: no cover
    SARIMAX = ExponentialSmoothing = None

try:
    from prophet import Prophet
except ImportError:                                    # pragma: no cover
    Prophet = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
CONFIG = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))

SCHEMA = CONFIG["schema"]
ANALYSIS = CONFIG["analysis"]
FORECAST = CONFIG["forecast"]
STEM = CONFIG["data"]["stem"]
OUT_DIR = ROOT / "data" / "pipeline" / STEM


# ─── LOAD & CLEAN ────────────────────────────────────────────────────────────

def to_number(series: pd.Series) -> pd.Series:
    """Ép về số, xử lý dấu phẩy dùng làm dấu thập phân (vd '5,6' → 5.6)."""
    if series.dtype.kind in "if":
        return series
    cleaned = (series.astype(str)
               .str.strip()
               .str.replace(r"[^\d,.\-]", "", regex=True))
    # Chỉ coi dấu phẩy là thập phân khi không có dấu chấm trong cùng giá trị
    has_dot = cleaned.str.contains(r"\.", na=False)
    cleaned = cleaned.where(has_dot, cleaned.str.replace(",", ".", regex=False))
    cleaned = cleaned.where(~has_dot, cleaned.str.replace(",", "", regex=False))
    return pd.to_numeric(cleaned, errors="coerce")


def load_data() -> tuple[pd.DataFrame, dict]:
    path = ROOT / CONFIG["data"]["file"]
    raw = (pd.read_excel(path, dtype=str) if path.suffix.lower() in {".xlsx", ".xls"}
           else pd.read_csv(path, dtype=str))

    issues: list[dict] = []
    df = raw.copy()

    # Ngày
    date_col = SCHEMA["date"]
    df[date_col] = pd.to_datetime(raw[date_col], format=SCHEMA.get("date_format"),
                                  errors="coerce")
    if df[date_col].isna().any():
        df[date_col] = pd.to_datetime(raw[date_col], errors="coerce", format="mixed")
    unparsed = int(df[date_col].isna().sum())
    if unparsed:
        issues.append({"severity": "high", "issue": f"{unparsed} dòng không parse được ngày",
                       "action": "loại khỏi phân tích"})
        df = df[df[date_col].notna()]

    # Cột số
    numeric_cols = [SCHEMA.get(k) for k in ("revenue", "profit", "quantity", "unit_price")]
    numeric_cols += SCHEMA.get("cost_columns") or []
    for col in [c for c in numeric_cols if c and c in df.columns]:
        before_comma = raw[col].astype(str).str.contains(",", na=False).sum()
        df[col] = to_number(raw.loc[df.index, col])
        if before_comma:
            issues.append({"severity": "medium",
                           "issue": f"{col}: {before_comma} dòng dùng dấu phẩy làm thập phân",
                           "action": "đã chuẩn hoá về dấu chấm"})
        if df[col].isna().any():
            issues.append({"severity": "medium",
                           "issue": f"{col}: {int(df[col].isna().sum())} giá trị không ép được về số",
                           "action": "coi như thiếu"})

    # Trùng khoá giao dịch
    txn = SCHEMA.get("transaction_id")
    if txn and txn in df.columns:
        dup_rows = int(df[txn].duplicated(keep=False).sum())
        if dup_rows:
            issues.append({"severity": "medium",
                           "issue": f"{txn}: {dup_rows} dòng thuộc nhóm ID trùng "
                                    f"({df[txn].nunique()} ID duy nhất / {len(df)} dòng)",
                           "action": "giữ nguyên — chưa rõ là upsert hay lỗi nhập"})

    # Lọc đơn hợp lệ
    status, valid = SCHEMA.get("status"), SCHEMA.get("status_valid")
    n_before = len(df)
    if status and status in df.columns and valid:
        excluded = int((df[status] != valid).sum())
        df = df[df[status] == valid]
        if excluded:
            issues.append({"severity": "info",
                           "issue": f"{excluded} đơn không ở trạng thái '{valid}'",
                           "action": f"loại khỏi phân tích doanh thu ({excluded/n_before:.1%})"})

    df["_period"] = df[date_col].dt.to_period(
        "M" if ANALYSIS.get("grain", "monthly") == "monthly" else "W")
    df["_year"] = df[date_col].dt.year
    return df, {"issues": issues, "rows_raw": len(raw), "rows_analyzed": len(df),
                "excluded_rows": len(raw) - len(df)}


def grade_confidence(meta: dict, df: pd.DataFrame, periods: int) -> dict:
    """Chấm điểm tin cậy — trừ điểm theo mức nghiêm trọng của từng vấn đề."""
    score = 100
    reasons = []
    weights = {"high": 15, "medium": 8, "low": 3, "info": 0}
    for issue in meta["issues"]:
        deduction = weights.get(issue["severity"], 0)
        score -= deduction
        if deduction:
            reasons.append(issue["issue"])

    min_periods = ANALYSIS.get("min_periods_for_trend", 12)
    if periods < min_periods:
        score -= 15
        reasons.append(f"chỉ có {periods} kỳ, dưới ngưỡng {min_periods} để kết luận xu hướng")

    # Kỳ cuối chưa trọn vẹn thì cảnh báo
    last_year_rows = (df["_year"] == df["_year"].max()).sum()
    typical = df.groupby("_year").size().median()
    if last_year_rows < typical * 0.75:
        score -= 8
        reasons.append(f"năm {int(df['_year'].max())} chỉ có {int(last_year_rows)} dòng "
                       f"(trung vị các năm: {int(typical)}) — kỳ chưa trọn vẹn")

    score = max(0, min(100, score))
    grade = ("A" if score >= 90 else "B" if score >= 80 else
             "C" if score >= 65 else "D" if score >= 50 else "F")
    return {"grade": grade, "score": score, "reasons": reasons}


# ─── DESCRIPTIVE ─────────────────────────────────────────────────────────────

def build_descriptive(df: pd.DataFrame) -> dict:
    rev, prof = SCHEMA["revenue"], SCHEMA.get("profit")
    qty, txn = SCHEMA.get("quantity"), SCHEMA.get("transaction_id")

    agg = {"revenue": (rev, "sum"), "orders": (rev, "size")}
    if prof:
        agg["profit"] = (prof, "sum")
    if qty:
        agg["units"] = (qty, "sum")
    monthly = df.groupby("_period").agg(**agg).reset_index()
    monthly["period"] = monthly["_period"].astype(str)
    monthly["aov"] = monthly["revenue"] / monthly["orders"]
    if prof:
        monthly["margin"] = monthly["profit"] / monthly["revenue"]

    # Xu hướng — hồi quy tuyến tính có kiểm định
    x = np.arange(len(monthly))
    reg = stats.linregress(x, monthly["revenue"].to_numpy())
    significant = bool(reg.pvalue < 0.05)
    min_periods = ANALYSIS.get("min_periods_for_trend", 12)
    trend = {
        "slope_per_period": float(reg.slope),
        "r_squared": float(reg.rvalue ** 2),
        "p_value": float(reg.pvalue),
        "significant": significant,
        "periods": int(len(monthly)),
        "verdict": ("không đủ kỳ để kết luận" if len(monthly) < min_periods
                    else "tăng có ý nghĩa thống kê" if significant and reg.slope > 0
                    else "giảm có ý nghĩa thống kê" if significant and reg.slope < 0
                    else "đi ngang — biến động không có ý nghĩa thống kê"),
    }

    # So sánh năm đầy đủ (loại năm chưa trọn vẹn)
    by_year = df.groupby("_year").agg(**agg)
    months_per_year = df.groupby("_year")["_period"].nunique()
    full_years = [int(y) for y in months_per_year.index if months_per_year[y] >= 12]
    yoy = {}
    if len(full_years) >= 2:
        prev, curr = full_years[-2], full_years[-1]
        yoy = {
            "prev_year": prev, "curr_year": curr,
            "revenue_prev": float(by_year.loc[prev, "revenue"]),
            "revenue_curr": float(by_year.loc[curr, "revenue"]),
            "revenue_change_pct": float((by_year.loc[curr, "revenue"] /
                                         by_year.loc[prev, "revenue"] - 1) * 100),
            "orders_change_pct": float((by_year.loc[curr, "orders"] /
                                        by_year.loc[prev, "orders"] - 1) * 100),
        }
        if prof:
            yoy["margin_prev"] = float(by_year.loc[prev, "profit"] / by_year.loc[prev, "revenue"])
            yoy["margin_curr"] = float(by_year.loc[curr, "profit"] / by_year.loc[curr, "revenue"])

    # So sánh cùng kỳ với năm chưa trọn vẹn (vd H1 vs H1)
    partial = [int(y) for y in months_per_year.index if months_per_year[y] < 12]
    partial_compare = {}
    if partial:
        p_year = partial[-1]
        p_months = set(df.loc[df["_year"] == p_year, "_period"].dt.month)
        if p_year - 1 in by_year.index:
            mask_curr = (df["_year"] == p_year)
            mask_prev = (df["_year"] == p_year - 1) & (df["_period"].dt.month.isin(p_months))
            rev_curr, rev_prev = df.loc[mask_curr, rev].sum(), df.loc[mask_prev, rev].sum()
            partial_compare = {
                "label": f"{sorted(p_months)[0]}-{sorted(p_months)[-1]}/{p_year} vs cùng kỳ {p_year-1}",
                "revenue_curr": float(rev_curr), "revenue_prev": float(rev_prev),
                "change_pct": float((rev_curr / rev_prev - 1) * 100) if rev_prev else None,
                "note": f"{p_year} chỉ có {months_per_year[p_year]} kỳ — không so cả năm được",
            }

    # Mùa vụ — chỉ dùng các năm trọn vẹn
    seasonality = {}
    if full_years and ANALYSIS.get("grain") == "monthly":
        full = df[df["_year"].isin(full_years)].copy()
        full["_month"] = full["_period"].dt.month
        by_month = full.groupby("_month")[rev].sum() / len(full_years)
        index = (by_month / by_month.mean() * 100).round(1)
        seasonality = {
            "index": {int(m): float(v) for m, v in index.items()},
            "peak_month": int(index.idxmax()), "peak_index": float(index.max()),
            "trough_month": int(index.idxmin()), "trough_index": float(index.min()),
            "swing_pp": float(index.max() - index.min()),
            "basis_years": full_years,
        }

    # Cắt lát theo chiều
    dimensions = {}
    top_n = ANALYSIS.get("top_n_dimensions", 5)
    for dim in SCHEMA.get("dimensions") or []:
        if dim not in df.columns:
            continue
        g = df.groupby(dim).agg(**agg)
        g["share_pct"] = g["revenue"] / g["revenue"].sum() * 100
        if len(full_years) >= 2:
            prev, curr = full_years[-2], full_years[-1]
            rev_prev = df[df["_year"] == prev].groupby(dim)[rev].sum()
            rev_curr = df[df["_year"] == curr].groupby(dim)[rev].sum()
            g["yoy_pct"] = ((rev_curr / rev_prev - 1) * 100).reindex(g.index)
            g["yoy_abs"] = (rev_curr - rev_prev).reindex(g.index)
        g = g.sort_values("revenue", ascending=False).head(top_n)
        dimensions[dim] = [
            {"name": str(name),
             "revenue": float(row["revenue"]),
             "orders": int(row["orders"]),
             "share_pct": float(row["share_pct"]),
             "yoy_pct": (None if "yoy_pct" not in g.columns or pd.isna(row.get("yoy_pct"))
                         else float(row["yoy_pct"])),
             "yoy_abs": (None if "yoy_abs" not in g.columns or pd.isna(row.get("yoy_abs"))
                         else float(row["yoy_abs"]))}
            for name, row in g.iterrows()
        ]

    totals = {
        "revenue": float(df[rev].sum()),
        "orders": int(len(df)),
        "aov": float(df[rev].sum() / len(df)),
        "period_start": str(df[SCHEMA["date"]].min().date()),
        "period_end": str(df[SCHEMA["date"]].max().date()),
        "periods": int(df["_period"].nunique()),
    }
    if prof:
        totals["profit"] = float(df[prof].sum())
        totals["margin"] = float(df[prof].sum() / df[rev].sum())
    if txn and txn in df.columns:
        totals["unique_transactions"] = int(df[txn].nunique())

    # AOV đầu kỳ vs cuối kỳ
    if len(full_years) >= 2:
        first, last = full_years[0], full_years[-1]
        aov_first = df[df["_year"] == first][rev].mean()
        aov_last = df[df["_year"] == last][rev].mean()
        totals["aov_first_year"] = float(aov_first)
        totals["aov_last_year"] = float(aov_last)
        totals["aov_change_pct"] = float((aov_last / aov_first - 1) * 100)

    return {
        "totals": totals,
        "monthly": monthly[[c for c in ("period", "revenue", "profit", "orders",
                                        "units", "aov", "margin") if c in monthly.columns]]
                   .round(4).to_dict("records"),
        "trend": trend,
        "yoy": yoy,
        "partial_compare": partial_compare,
        "seasonality": seasonality,
        "dimensions": dimensions,
    }


# ─── DIAGNOSTIC ──────────────────────────────────────────────────────────────

def build_diagnostic(df: pd.DataFrame, desc: dict) -> dict:
    rev = SCHEMA["revenue"]
    yoy = desc.get("yoy") or {}
    if not yoy:
        return {"note": "Không đủ hai năm trọn vẹn để phân tích nguyên nhân biến động."}

    prev, curr = yoy["prev_year"], yoy["curr_year"]
    total_change = yoy["revenue_curr"] - yoy["revenue_prev"]

    # Đóng góp vào biến động theo từng chiều
    contributions = {}
    for dim in SCHEMA.get("dimensions") or []:
        if dim not in df.columns:
            continue
        a = df[df["_year"] == prev].groupby(dim)[rev].sum()
        b = df[df["_year"] == curr].groupby(dim)[rev].sum()
        delta = (b.reindex(a.index.union(b.index), fill_value=0)
                 - a.reindex(a.index.union(b.index), fill_value=0))
        delta = delta.sort_values()
        contributions[dim] = [
            {"name": str(k), "delta": float(v),
             "pct_of_total_change": (float(v / total_change * 100) if total_change else None)}
            for k, v in delta.items()
        ]

    # Simpson's paradox — hướng biến động tổng có nhất quán trên từng nhóm không
    paradox = {}
    agg_direction = np.sign(total_change)
    for dim, rows in contributions.items():
        directions = {r["name"]: np.sign(r["delta"]) for r in rows}
        against = [n for n, d in directions.items() if d != 0 and d != agg_direction]
        paradox[dim] = {
            "aggregate_direction": "giảm" if agg_direction < 0 else "tăng",
            "groups_against_trend": against,
            "consistent": len(against) == 0,
            "note": ("mọi nhóm cùng hướng với tổng — không có nghịch lý Simpson"
                     if not against else
                     f"{len(against)}/{len(directions)} nhóm đi ngược hướng tổng: "
                     f"{', '.join(against)}"),
        }

    # Tách biến động thành hiệu ứng sản lượng vs giá trị đơn
    orders_prev = int((df["_year"] == prev).sum())
    orders_curr = int((df["_year"] == curr).sum())
    aov_prev = yoy["revenue_prev"] / orders_prev
    aov_curr = yoy["revenue_curr"] / orders_curr
    volume_effect = (orders_curr - orders_prev) * aov_prev
    price_effect = (aov_curr - aov_prev) * orders_curr
    decomposition = {
        "total_change": float(total_change),
        "volume_effect": float(volume_effect),
        "price_effect": float(price_effect),
        "volume_share_pct": (float(abs(volume_effect) /
                                   (abs(volume_effect) + abs(price_effect)) * 100)
                             if (volume_effect or price_effect) else None),
        "orders_prev": orders_prev, "orders_curr": orders_curr,
        "aov_prev": float(aov_prev), "aov_curr": float(aov_curr),
        "driver": ("sản lượng" if abs(volume_effect) > abs(price_effect)
                   else "giá trị đơn"),
    }

    # Tập trung rủi ro
    concentration = {}
    for dim, rows in (desc.get("dimensions") or {}).items():
        if rows:
            concentration[dim] = {
                "top1_name": rows[0]["name"],
                "top1_share_pct": rows[0]["share_pct"],
                "top2_share_pct": sum(r["share_pct"] for r in rows[:2]),
                "risk": ("cao" if rows[0]["share_pct"] > 60 else
                         "trung bình" if rows[0]["share_pct"] > 40 else "thấp"),
            }

    return {
        "compare": {"prev_year": prev, "curr_year": curr, "total_change": float(total_change)},
        "contributions": contributions,
        "simpsons_paradox": paradox,
        "decomposition": decomposition,
        "concentration": concentration,
    }


# ─── PREDICTIVE ──────────────────────────────────────────────────────────────

def seasonal_naive(series: np.ndarray, horizon: int, season: int = 12,
                   labels: list | None = None) -> np.ndarray:
    """Baseline: lặp lại giá trị cùng kỳ mùa trước."""
    out = []
    history = list(series)
    for i in range(horizon):
        idx = len(history) - season + i if len(history) >= season else -1
        out.append(history[idx] if len(history) >= season else history[-1])
    return np.array(out, dtype=float)


def trend_seasonal(series: np.ndarray, horizon: int, season: int = 12,
                   labels: list | None = None) -> np.ndarray:
    """Hồi quy xu hướng nhân với chỉ số mùa vụ."""
    x = np.arange(len(series))
    reg = stats.linregress(x, series)
    fitted = reg.intercept + reg.slope * x
    ratio = np.divide(series, fitted, out=np.ones_like(series), where=fitted != 0)
    idx = np.array([ratio[i::season].mean() if len(ratio[i::season]) else 1.0
                    for i in range(season)])
    idx = idx / idx.mean()
    future_x = np.arange(len(series), len(series) + horizon)
    base = reg.intercept + reg.slope * future_x
    return base * np.array([idx[i % season] for i in range(len(series),
                                                          len(series) + horizon)])


def moving_average(series: np.ndarray, horizon: int, season: int = 12,
                   labels: list | None = None, window: int = 3) -> np.ndarray:
    return np.repeat(series[-window:].mean(), horizon)


def sarima(series: np.ndarray, horizon: int, season: int = 12,
           labels: list | None = None) -> np.ndarray:
    """SARIMA(1,1,1)(1,1,0,s) — cần statsmodels."""
    if SARIMAX is None:
        raise RuntimeError("statsmodels chưa được cài")
    # Bậc mùa vụ chọn theo độ dài chuỗi. Sai phân mùa vụ (D=1) ăn mất trọn một
    # chu kỳ quan sát, nên chỉ dùng khi có từ 3 chu kỳ trở lên; 2 chu kỳ thì
    # dùng AR mùa vụ không sai phân, dưới nữa thì bỏ hẳn thành phần mùa vụ.
    if len(series) >= season * 3:
        seasonal_order = (1, 1, 0, season)
    elif len(series) >= season * 2:
        seasonal_order = (1, 0, 0, season)
    else:
        seasonal_order = (0, 0, 0, 0)
    model = SARIMAX(series, order=(1, 1, 1), seasonal_order=seasonal_order,
                    enforce_stationarity=False, enforce_invertibility=False)
    fitted = model.fit(disp=False)
    return np.asarray(fitted.forecast(steps=horizon), dtype=float)


def holt_winters(series: np.ndarray, horizon: int, season: int = 12,
                 labels: list | None = None) -> np.ndarray:
    """Holt-Winters cộng tính — cần statsmodels."""
    if ExponentialSmoothing is None:
        raise RuntimeError("statsmodels chưa được cài")
    use_seasonal = len(series) >= season * 2
    model = ExponentialSmoothing(
        series, trend="add",
        seasonal="add" if use_seasonal else None,
        seasonal_periods=season if use_seasonal else None,
        initialization_method="estimated")
    return np.asarray(model.fit().forecast(horizon), dtype=float)


def prophet_model(series: np.ndarray, horizon: int, season: int = 12,
                  labels: list | None = None) -> np.ndarray:
    """Prophet — cần prophet + cột ngày thật, nên bắt buộc có `labels`."""
    if Prophet is None:
        raise RuntimeError("prophet chưa được cài")
    if not labels:
        raise RuntimeError("prophet cần nhãn thời gian, không có labels")
    freq = "MS" if season == 12 else "W"
    history = pd.DataFrame({
        "ds": pd.PeriodIndex(labels, freq="M" if season == 12 else "W").to_timestamp(),
        "y": series,
    })
    model = Prophet(yearly_seasonality=(season == 12), weekly_seasonality=False,
                    daily_seasonality=False, interval_width=0.8)
    model.fit(history)
    future = model.make_future_dataframe(periods=horizon, freq=freq)
    return np.asarray(model.predict(future)["yhat"].to_numpy()[-horizon:], dtype=float)


# Tên trong config.yaml → hàm. Thiếu thư viện thì hàm tự raise và bị loại
# khỏi backtest, không làm hỏng cả pipeline.
MODELS = {
    "seasonal_naive": seasonal_naive,
    "trend_seasonal": trend_seasonal,
    "moving_average": moving_average,
    "sarima": sarima,
    "holt_winters": holt_winters,
    "prophet": prophet_model,
}

# Baseline luôn phải chạy để có mốc so sánh, dù config có liệt kê hay không
BASELINE_MODEL = "seasonal_naive"


def mape(actual: np.ndarray, pred: np.ndarray) -> float:
    mask = actual != 0
    return float(np.mean(np.abs((actual[mask] - pred[mask]) / actual[mask])) * 100)


def build_predictive(desc: dict) -> dict:
    if not FORECAST.get("enabled", True):
        return {"enabled": False}

    monthly = pd.DataFrame(desc["monthly"])
    target = "revenue" if FORECAST.get("target", "revenue") == "revenue" else "profit"
    series = monthly[target].to_numpy(dtype=float)
    labels = monthly["period"].tolist()
    horizon = int(FORECAST.get("horizon", 6))
    season = 12 if ANALYSIS.get("grain") == "monthly" else 52

    if len(series) < season + horizon:
        holdout = max(3, min(horizon, len(series) // 5))
    else:
        holdout = horizon

    train, test = series[:-holdout], series[-holdout:]
    train_labels = labels[:-holdout]

    # Model nào chạy: theo config, cộng baseline (luôn có để làm mốc so sánh)
    requested = list(FORECAST.get("models") or [])
    if BASELINE_MODEL not in requested:
        requested.insert(0, BASELINE_MODEL)
    unknown = [m for m in requested if m not in MODELS]
    to_run = [m for m in requested if m in MODELS]

    # Backtest — mọi model chạy trên cùng một tập train/test
    results = []
    for name in to_run:
        try:
            pred = MODELS[name](train, holdout, season, train_labels)
            if len(pred) != holdout or not np.all(np.isfinite(pred)):
                raise ValueError(f"trả về {len(pred)} giá trị không hợp lệ")
            results.append({"model": name, "mape": round(mape(test, pred), 2),
                            "available": True})
        except Exception as exc:                       # model lỗi thì loại, không chặn pipeline
            results.append({"model": name, "mape": None, "available": False,
                            "error": f"{type(exc).__name__}: {exc}"})
            print(f"  ! model {name} không chạy được: {type(exc).__name__}: {exc}")
    for name in unknown:
        results.append({"model": name, "mape": None, "available": False,
                        "error": "không có trong compute_metrics.MODELS"})

    scored = [r for r in results if r["mape"] is not None]
    if not scored:
        raise SystemExit("Không model dự báo nào chạy được — kiểm tra log ở trên. "
                         "Cài statsmodels/prophet hoặc tắt forecast trong config.yaml.")
    scored.sort(key=lambda r: r["mape"])
    best = scored[0]
    baseline = next((r for r in scored if r["model"] == BASELINE_MODEL), None)

    # Quy tắc: không thắng được baseline thì dùng baseline
    if baseline and best["model"] != BASELINE_MODEL and best["mape"] >= baseline["mape"]:
        best = baseline
    chosen = best["model"]

    # Refit trên toàn bộ chuỗi. Model thắng backtest mà lỗi khi refit thì lùi
    # về baseline, không để pipeline chết ở bước cuối.
    try:
        point = MODELS[chosen](series, horizon, season, labels)
        if not np.all(np.isfinite(point)):
            raise ValueError("dự báo chứa giá trị không hợp lệ")
    except Exception as exc:
        print(f"  ! {chosen} lỗi khi refit toàn chuỗi ({exc}) — lùi về {BASELINE_MODEL}")
        chosen = BASELINE_MODEL
        best = baseline or {"model": BASELINE_MODEL, "mape": None}
        point = MODELS[BASELINE_MODEL](series, horizon, season, labels)

    # Khoảng tin cậy từ sai số backtest. Không có MAPE (trường hợp lùi về
    # baseline sau lỗi refit) thì dùng 15% — rộng, và được ghi vào phần rủi ro.
    resid_pct = (best["mape"] / 100) if best.get("mape") is not None else 0.15
    z = {0.80: 1.282, 0.90: 1.645, 0.95: 1.960}.get(
        float(FORECAST.get("confidence_interval", 0.80)), 1.282)
    margin = point * resid_pct * z

    last_period = pd.Period(labels[-1], freq="M" if ANALYSIS.get("grain") == "monthly" else "W")
    future_labels = [str(last_period + i) for i in range(1, horizon + 1)]

    # In bảng so sánh — để log của mỗi lần chạy tự trả lời "model nào thắng"
    print(f"\n  Backtest: {len(train)} kỳ train / {holdout} kỳ test")
    for r in sorted(results, key=lambda r: (r["mape"] is None, r["mape"] or 0)):
        if r["mape"] is None:
            print(f"    {r['model']:16}    —      loại ({r['error']})")
        else:
            mark = "← chọn" if r["model"] == chosen else ""
            base = " (baseline)" if r["model"] == BASELINE_MODEL else ""
            print(f"    {r['model']:16} MAPE {r['mape']:6.2f}%{base:12} {mark}")
    if baseline and baseline["mape"] is not None and chosen != BASELINE_MODEL:
        gain = baseline["mape"] - best["mape"]
        print(f"    → {chosen} tốt hơn baseline {gain:.2f} điểm MAPE")
    elif chosen == BASELINE_MODEL:
        print("    → không model nào thắng baseline, dùng baseline")

    return {
        "enabled": True,
        "target": target,
        "horizon": horizon,
        "chosen_model": chosen,
        "chosen_mape": best["mape"],
        "baseline_model": BASELINE_MODEL,
        "baseline_mape": baseline["mape"] if baseline else None,
        "beat_baseline": bool(baseline and chosen != BASELINE_MODEL),
        "backtest": {"train_periods": len(train), "test_periods": holdout,
                     "results": results},
        "history": [{"period": p, "value": float(v)} for p, v in zip(labels, series)],
        "points": [{"period": p, "value": float(v), "lo": float(max(0, v - m)),
                    "hi": float(v + m)}
                   for p, v, m in zip(future_labels, point, margin)],
        "total_forecast": float(point.sum()),
        # Model được yêu cầu nhưng không chạy được — kèm lý do, để phần rủi ro
        # của report nói đúng chuyện gì đã xảy ra thay vì im lặng bỏ qua.
        "unavailable_models": [r["model"] for r in results if not r["available"]],
        "unavailable_detail": {r["model"]: r["error"]
                               for r in results if not r["available"]},
    }


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df, meta = load_data()
    print(f"Đã nạp {meta['rows_raw']} dòng → {meta['rows_analyzed']} dòng phân tích")

    desc = build_descriptive(df)
    confidence = grade_confidence(meta, df, desc["totals"]["periods"])
    profile = {"generated_at": date.today().isoformat(), **meta, "confidence": confidence}

    diag = build_diagnostic(df, desc)
    pred = build_predictive(desc)

    for name, payload in (("profile", profile), ("descriptive_output", desc),
                          ("diagnostic_output", diag), ("predictive_output", pred)):
        path = OUT_DIR / f"{name}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str),
                        encoding="utf-8")
        print(f"  ✓ {path.relative_to(ROOT)}")

    print(f"\nĐộ tin cậy: {confidence['grade']} ({confidence['score']}/100)")
    if confidence["grade"] == "F":
        print("Grade F — data không đủ chất lượng để kết luận. Dừng.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
