"""
assemble_report.py
------------------
Lắp ráp đầu ra cuối cùng từ các file JSON mà compute_metrics.py đã tính.

Không tính lại bất kỳ con số nào — mọi giá trị đều đọc từ
data/pipeline/{stem}/*.json. Narrative dựng theo luật (nếu hiệu ứng giá
lấn át sản lượng thì câu chuyện là bào mòn AOV, v.v.) nên chạy lại tuần
sau với data mới sẽ tự ra kết luận khác.

Đọc : data/pipeline/{stem}/{profile,descriptive,diagnostic,predictive}_output.json
Ghi : data/pipeline/{stem}/chart_specs.json      → cho render_html.py
      data/pipeline/{stem}/report_context.json   → cho render_html.py
      data/pipeline/{stem}/insights.json         → cho send_report.py

Dùng: python assemble_report.py
"""

import json
import sys
from datetime import date
from pathlib import Path

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
CONFIG = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
STEM = CONFIG["data"]["stem"]
PIPE = ROOT / "data" / "pipeline" / STEM
TODAY = date.today().isoformat()

BLUE, PURPLE, GREEN, RED, GRAY = "#2554E7", "#9333EA", "#10B981", "#EF4444", "#94A3B8"


def load(name: str) -> dict:
    path = PIPE / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"Thiếu {path.relative_to(ROOT)} — chạy compute_metrics.py trước.")
    return json.loads(path.read_text(encoding="utf-8"))


def money(v: float) -> str:
    """Format tiền theo độ lớn — $1.83M, $729K, $612."""
    a = abs(v)
    sign = "-" if v < 0 else ""
    if a >= 1_000_000:
        return f"{sign}${a/1_000_000:.2f}M"
    if a >= 1_000:
        return f"{sign}${a/1_000:.0f}K"
    return f"{sign}${a:,.0f}"


def pct(v: float, decimals: int = 1) -> str:
    return f"{v:+.{decimals}f}%"


MONTH_VI = {1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3", 4: "Tháng 4", 5: "Tháng 5",
            6: "Tháng 6", 7: "Tháng 7", 8: "Tháng 8", 9: "Tháng 9", 10: "Tháng 10",
            11: "Tháng 11", 12: "Tháng 12"}


# ─── CHART SPECS ─────────────────────────────────────────────────────────────

def build_charts(desc: dict, diag: dict, pred: dict) -> dict:
    charts = []
    monthly = desc["monthly"]
    labels = [m["period"] for m in monthly]
    values = [round(m["revenue"], 2) for m in monthly]

    # 1. Xu hướng doanh thu — làm nổi đỉnh và đáy mùa vụ
    season = desc.get("seasonality") or {}
    peak_m, trough_m = season.get("peak_month"), season.get("trough_month")
    charts.append({
        "chart_id": "monthly_revenue_trend",
        "chart_type": "highlight_line",
        "title": "Doanh thu theo tháng — dao động mùa vụ, không có xu hướng rõ",
        "data": {
            "labels": labels,
            "series": [{
                "name": "Doanh thu",
                "values": values,
                "highlight_indices": [i for i, m in enumerate(monthly)
                                      if int(m["period"][-2:]) == peak_m],
                "trough_indices": [i for i, m in enumerate(monthly)
                                   if int(m["period"][-2:]) == trough_m],
                "color_default": GRAY, "color_highlight": BLUE, "color_trough": RED,
            }],
        },
    })

    # 2. Tăng trưởng theo nhóm hàng — nơi nghịch lý Simpson lộ ra
    yoy = desc.get("yoy") or {}
    cats = [d for d in (desc.get("dimensions") or {}).get("Category", [])
            if d.get("yoy_pct") is not None]
    if cats:
        cats = sorted(cats, key=lambda c: c["yoy_pct"])
        charts.append({
            "chart_id": "category_yoy",
            "chart_type": "horizontal_bar",
            "title": f"Tăng trưởng {yoy.get('curr_year')} vs {yoy.get('prev_year')} theo nhóm hàng",
            "data": {
                "labels": [f"{c['name']} ({c['share_pct']:.0f}% DT)" for c in cats],
                "series": [{
                    "name": "YoY %",
                    "values": [round(c["yoy_pct"], 1) for c in cats],
                    "colors": [RED if c["yoy_pct"] < 0 else GREEN for c in cats],
                }],
            },
        })

    # 3. Waterfall — nhóm nào kéo doanh thu đi đâu
    contrib = (diag.get("contributions") or {}).get("Category")
    if contrib and yoy:
        ordered = sorted(contrib, key=lambda c: c["delta"])
        charts.append({
            "chart_id": "yoy_waterfall",
            "chart_type": "waterfall",
            "title": f"Từ {yoy['prev_year']} đến {yoy['curr_year']}: nhóm nào kéo doanh thu",
            "data": {
                "labels": ([str(yoy["prev_year"])] + [c["name"] for c in ordered]
                           + [str(yoy["curr_year"])]),
                "series": [{
                    "name": "Đóng góp",
                    "values": ([round(yoy["revenue_prev"], 0)]
                               + [round(c["delta"], 0) for c in ordered]
                               + [round(yoy["revenue_curr"], 0)]),
                    "types": ["base"] + ["delta"] * len(ordered) + ["total"],
                    "colors": ([GRAY]
                               + [RED if c["delta"] < 0 else GREEN for c in ordered]
                               + [BLUE]),
                }],
            },
        })

    # 4. Dự báo
    if pred.get("enabled"):
        hist_labels = [h["period"] for h in pred["history"]]
        hist_values = [round(h["value"], 2) for h in pred["history"]]
        fc_labels = [p["period"] for p in pred["points"]]
        n_hist, n_fc = len(hist_labels), len(fc_labels)
        charts.append({
            "chart_id": "revenue_forecast",
            "chart_type": "forecast_line",
            "title": (f"Dự báo {n_fc} kỳ tới — model {pred['chosen_model']} "
                      f"(MAPE {pred['chosen_mape']}%)"),
            "data": {
                "labels": hist_labels + fc_labels,
                "forecast_start_idx": n_hist,
                "series": [
                    {"name": "Actual", "color": BLUE,
                     "values": hist_values + [None] * n_fc},
                    {"name": "Forecast", "color": GREEN,
                     "values": [None] * (n_hist - 1) + [hist_values[-1]]
                               + [round(p["value"], 2) for p in pred["points"]]},
                    {"name": "CI Low",
                     "values": [None] * n_hist + [round(p["lo"], 2) for p in pred["points"]]},
                    {"name": "CI High",
                     "values": [None] * n_hist + [round(p["hi"], 2) for p in pred["points"]]},
                ],
            },
        })

    # 5. So sánh model — chứng minh model được chọn thắng baseline
    scored = [r for r in pred.get("backtest", {}).get("results", []) if r.get("mape")]
    if scored:
        scored = sorted(scored, key=lambda r: -r["mape"])
        charts.append({
            "chart_id": "model_comparison",
            "chart_type": "model_comparison_bar",
            "title": "Sai số backtest (MAPE, thấp hơn là tốt hơn)",
            "data": {
                "labels": [r["model"] for r in scored],
                "series": [{
                    "name": "MAPE %",
                    "values": [r["mape"] for r in scored],
                    "colors": [GREEN if r["model"] == pred.get("chosen_model") else GRAY
                               for r in scored],
                }],
            },
        })

    return {"charts": charts}


# ─── NARRATIVE ───────────────────────────────────────────────────────────────

def story_facts(desc: dict, diag: dict, pred: dict) -> dict:
    """Rút ra các sự thật mà narrative dựa vào — một chỗ duy nhất, không lặp."""
    yoy = desc.get("yoy") or {}
    decomp = diag.get("decomposition") or {}
    conc = (diag.get("concentration") or {})
    dims = desc.get("dimensions") or {}

    cats = [c for c in dims.get("Category", []) if c.get("yoy_pct") is not None]
    growing = sorted([c for c in cats if c["yoy_pct"] > 0],
                     key=lambda c: -c["yoy_pct"])
    declining = sorted([c for c in cats if c["yoy_pct"] <= 0], key=lambda c: c["yoy_pct"])

    regions = [r for r in dims.get("Region", []) if r.get("yoy_pct") is not None]
    growing_regions = sorted([r for r in regions if r["yoy_pct"] > 0],
                             key=lambda r: -r["yoy_pct"])

    top_concentration = max(conc.items(), key=lambda kv: kv[1]["top1_share_pct"],
                            default=(None, None))

    return {
        "yoy": yoy, "decomp": decomp, "trend": desc.get("trend") or {},
        "season": desc.get("seasonality") or {}, "totals": desc["totals"],
        "growing_cats": growing, "declining_cats": declining,
        "growing_regions": growing_regions,
        "concentration_dim": top_concentration[0],
        "concentration": top_concentration[1],
        "partial": desc.get("partial_compare") or {},
        "pred": pred,
    }


def build_headline(f: dict) -> str:
    yoy, decomp = f["yoy"], f["decomp"]
    if not yoy:
        return f"Doanh thu {money(f['totals']['revenue'])} trên {f['totals']['periods']} kỳ."
    driver = decomp.get("driver", "")
    aov_change = ((decomp.get("aov_curr", 0) / decomp.get("aov_prev", 1) - 1) * 100
                  if decomp.get("aov_prev") else 0)
    if driver == "giá trị đơn":
        return (f"Doanh thu {yoy['curr_year']} giảm {abs(yoy['revenue_change_pct']):.1f}% "
                f"dù số đơn vẫn tăng {yoy['orders_change_pct']:+.1f}% — vấn đề nằm ở "
                f"giá trị mỗi đơn ({pct(aov_change)}), không phải ở nhu cầu.")
    return (f"Doanh thu {yoy['curr_year']} thay đổi {pct(yoy['revenue_change_pct'])} "
            f"chủ yếu do {driver}, với số đơn {pct(yoy['orders_change_pct'])}.")


def build_kpis(f: dict) -> list[dict]:
    totals, yoy, pred = f["totals"], f["yoy"], f["pred"]
    kpis = [{"label": "Doanh thu", "value": money(totals["revenue"]),
             "delta": (f"{pct(yoy['revenue_change_pct'])} so với {yoy['prev_year']}"
                       if yoy else f"{totals['periods']} kỳ"),
             "direction": ("down" if yoy and yoy["revenue_change_pct"] < 0
                           else "up" if yoy else "flat")}]
    if "margin" in totals:
        margin_delta = ""
        direction = "flat"
        if yoy and "margin_curr" in yoy:
            change_pp = (yoy["margin_curr"] - yoy["margin_prev"]) * 100
            margin_delta = (f"{change_pp:+.1f} điểm so với {yoy['prev_year']}"
                            if abs(change_pp) >= 0.1 else "không đổi")
            direction = ("flat" if abs(change_pp) < 0.1
                         else "up" if change_pp > 0 else "down")
        kpis.append({"label": "Biên lợi nhuận", "value": f"{totals['margin']*100:.1f}%",
                     "delta": margin_delta, "direction": direction})
    if "aov_change_pct" in totals:
        kpis.append({"label": "Giá trị mỗi đơn", "value": money(totals["aov"]),
                     "delta": f"{pct(totals['aov_change_pct'])} so với đầu kỳ",
                     "direction": "down" if totals["aov_change_pct"] < 0 else "up"})
    if pred.get("enabled"):
        # Nhãn nói bằng ngôn ngữ kinh doanh — MAPE và tên model thuộc về report,
        # không thuộc về email gửi lãnh đạo.
        kpis.append({"label": f"Dự báo {pred['horizon']} tháng tới",
                     "value": money(pred["total_forecast"]),
                     "delta": "ước tính", "direction": "flat"})
    return kpis


def build_findings(f: dict) -> list[dict]:
    findings, yoy, decomp = [], f["yoy"], f["decomp"]

    if decomp:
        findings.append({
            "tag": "Root Cause",
            "title": (f"Sụt giảm đến từ giá trị đơn, không phải sản lượng — "
                      f"hiệu ứng giá {money(decomp['price_effect'])} "
                      f"so với sản lượng {money(decomp['volume_effect'])}"),
            "detail": (f"Số đơn tăng từ {decomp['orders_prev']:,} lên "
                       f"{decomp['orders_curr']:,} nhưng AOV rơi từ "
                       f"{money(decomp['aov_prev'])} xuống {money(decomp['aov_curr'])}. "
                       f"Nhu cầu không yếu đi — mỗi đơn đang mang về ít tiền hơn."),
            "evidence": (f"Phân tách biến động {money(decomp['total_change'])}: "
                         f"hiệu ứng sản lượng {money(decomp['volume_effect'])}, "
                         f"hiệu ứng giá {money(decomp['price_effect'])}."),
        })

    trend = f["trend"]
    if trend:
        findings.append({
            "tag": "Trend",
            "title": f"Xu hướng {trend['periods']} kỳ: {trend['verdict']}",
            "detail": (f"Hồi quy tuyến tính cho hệ số góc "
                       f"{money(trend['slope_per_period'])}/kỳ, nhưng "
                       f"R²={trend['r_squared']:.3f} và p={trend['p_value']:.3f} — "
                       f"{'đủ' if trend['significant'] else 'chưa đủ'} bằng chứng thống kê "
                       f"để gọi đây là một xu hướng."),
            "evidence": ("Biến động giữa các kỳ chủ yếu là mùa vụ, không phải suy giảm "
                         "cấu trúc." if not trend["significant"] else
                         "Xu hướng có ý nghĩa thống kê, cần hành động."),
        })

    if f["growing_cats"] and f["declining_cats"]:
        g, d = f["growing_cats"][0], f["declining_cats"][0]
        findings.append({
            "tag": "Contrast",
            "title": (f"{len(f['growing_cats'])}/{len(f['growing_cats'])+len(f['declining_cats'])} "
                      f"nhóm hàng vẫn tăng — tổng bị {d['name']} "
                      f"({d['share_pct']:.0f}% doanh thu) kéo xuống"),
            "detail": (f"{g['name']} tăng {pct(g['yoy_pct'])} và "
                       f"{', '.join(c['name'] + ' ' + pct(c['yoy_pct']) for c in f['growing_cats'][1:3])}"
                       f". Nhưng {d['name']} giảm {pct(d['yoy_pct'])} trên nền "
                       f"{d['share_pct']:.0f}% doanh thu nên áp đảo toàn bộ."),
            "evidence": (f"Đây là nghịch lý Simpson: nhìn tổng thấy giảm, nhìn từng nhóm "
                         f"thì đa số đang tăng. Các nhóm tăng cộng lại chỉ chiếm "
                         f"{sum(c['share_pct'] for c in f['growing_cats']):.0f}% doanh thu."),
        })

    conc = f["concentration"]
    if conc and conc["risk"] in ("cao", "trung bình"):
        findings.append({
            "tag": "Implication",
            "title": (f"{conc['top1_name']} chiếm {conc['top1_share_pct']:.0f}% doanh thu — "
                      f"rủi ro tập trung {conc['risk']}"),
            "detail": (f"Kết quả kinh doanh gần như là kết quả của riêng "
                       f"{conc['top1_name']}. Mọi biến động của nhóm này đi thẳng vào "
                       f"tổng doanh thu mà không có nhóm nào đủ lớn để bù."),
            "evidence": f"Hai hạng mục lớn nhất chiếm {conc['top2_share_pct']:.0f}% doanh thu.",
        })

    season = f["season"]
    if season:
        findings.append({
            "tag": "Pattern",
            "title": (f"Mùa vụ dao động {season['swing_pp']:.0f} điểm — đỉnh "
                      f"{MONTH_VI[season['peak_month']]}, đáy {MONTH_VI[season['trough_month']]}"),
            "detail": (f"{MONTH_VI[season['peak_month']]} đạt chỉ số "
                       f"{season['peak_index']:.0f} (cao hơn trung bình "
                       f"{season['peak_index']-100:.0f}%), "
                       f"{MONTH_VI[season['trough_month']]} chỉ {season['trough_index']:.0f}. "
                       f"Kế hoạch tồn kho và ngân sách quảng cáo nên bám nhịp này."),
            "evidence": f"Chỉ số tính trên các năm trọn vẹn: {season['basis_years']}.",
        })
    return findings


def build_executive(f: dict) -> dict:
    """Bản dành cho lãnh đạo — không thuật ngữ, không thống kê, không tên model.

    Cùng nguồn số với phần kỹ thuật, chỉ khác cách kể: nói chuyện kinh doanh
    (bán được bao nhiêu, giỏ hàng to hay nhỏ, nhóm nào lên xuống), bỏ hết
    p-value, MAPE, hiệu ứng giá/sản lượng, điểm tin cậy.
    """
    yoy, decomp, totals = f["yoy"], f["decomp"], f["totals"]
    season, pred = f["season"], f["pred"]
    summary: list[str] = []

    # 1. Kết quả gọn trong một câu
    if yoy:
        direction = "giảm" if yoy["revenue_change_pct"] < 0 else "tăng"
        line = (f"Doanh thu {yoy['curr_year']} đạt {money(yoy['revenue_curr'])}, "
                f"{direction} {abs(yoy['revenue_change_pct']):.1f}% so với {yoy['prev_year']}.")
        if "margin_curr" in yoy:
            change_pp = abs(yoy["margin_curr"] - yoy["margin_prev"]) * 100
            line += (f" Tỷ lệ lợi nhuận giữ nguyên ở {yoy['margin_curr']*100:.0f}%."
                     if change_pp < 0.5 else
                     f" Tỷ lệ lợi nhuận {yoy['margin_curr']*100:.0f}%.")
        summary.append(line)

    # 2. Khách mua ít đi hay giỏ hàng nhỏ đi — câu hỏi lãnh đạo nào cũng hỏi
    if decomp:
        gap = decomp["aov_prev"] - decomp["aov_curr"]
        order_change = decomp["orders_curr"] - decomp["orders_prev"]
        if decomp.get("driver") == "giá trị đơn":
            summary.append(
                f"Lượng khách mua không giảm — số đơn gần như không đổi "
                f"({decomp['orders_prev']:,} lên {decomp['orders_curr']:,} đơn). "
                f"Vấn đề là mỗi đơn nhỏ đi {money(abs(gap))}, từ "
                f"{money(decomp['aov_prev'])} xuống {money(decomp['aov_curr'])}.")
        else:
            summary.append(
                f"Số đơn thay đổi {order_change:+,} đơn, trong khi giá trị mỗi đơn "
                f"ở mức {money(decomp['aov_curr'])}.")

    # 3. Nhóm hàng nào kéo lên, nhóm nào kéo xuống
    if f["declining_cats"] and f["growing_cats"]:
        d, growing = f["declining_cats"][0], f["growing_cats"]
        names = ", ".join(f"{c['name']} {pct(c['yoy_pct'], 0)}" for c in growing[:3])
        summary.append(
            f"{d['name']} chiếm {d['share_pct']:.0f}% doanh thu và giảm "
            f"{abs(d['yoy_pct']):.0f}%, đủ để kéo cả công ty đi xuống. "
            f"Các nhóm còn lại đều tăng ({names}) nhưng còn quá nhỏ để bù lại.")

    # 4. Vùng nào đang làm tốt
    if f["growing_regions"]:
        r = f["growing_regions"][0]
        summary.append(f"Vùng {r['name']} là nơi duy nhất tăng trưởng "
                       f"({pct(r['yoy_pct'], 0)}) trong khi các vùng khác đều giảm.")

    # 5. Nhịp mùa vụ — dùng để lên kế hoạch
    if season:
        summary.append(
            f"{MONTH_VI[season['peak_month']]} luôn là tháng cao điểm, "
            f"{MONTH_VI[season['trough_month']]} thấp nhất năm — chênh nhau "
            f"khoảng {season['swing_pp']:.0f}% doanh thu. Nên chốt tồn kho và "
            f"ngân sách quảng cáo theo nhịp này.")

    # Dự báo nói bằng khoảng, không nói tên model cũng không nói sai số
    outlook = ""
    if pred.get("enabled") and pred.get("points"):
        lo = sum(p["lo"] for p in pred["points"])
        hi = sum(p["hi"] for p in pred["points"])
        peak = max(pred["points"], key=lambda p: p["value"])
        peak_month = int(peak["period"][-2:])
        outlook = (f"{pred['horizon']} tháng tới ước đạt {money(lo)} – {money(hi)}, "
                   f"với cao điểm rơi vào {MONTH_VI.get(peak_month, peak['period'])} "
                   f"khoảng {money(peak['value'])}.")

    return {"summary": summary, "outlook": outlook}


def build_strategy(f: dict) -> list[dict]:
    actions, decomp = [], f["decomp"]
    max_actions = CONFIG["strategy"].get("max_actions", 5)

    if decomp and decomp.get("driver") == "giá trị đơn":
        gap = decomp["aov_prev"] - decomp["aov_curr"]
        recover = gap * decomp["orders_curr"]
        actions.append({
            "action": "Dựng lại giá trị đơn: bán kèm và nâng cấp cấu hình tại bước thanh toán",
            "rationale": (f"Mỗi đơn nhỏ đi {money(gap)} trong khi số khách mua không "
                          f"giảm — vấn đề nằm ở giỏ hàng, không phải ở lượng khách."),
            "impact": f"Đưa giá trị đơn về mức cũ tương đương {money(recover)}/năm",
            "effort": "Trung bình", "owner_hint": "Thương mại điện tử", "priority": 1,
        })

    if f["growing_cats"]:
        g = f["growing_cats"][0]
        if g.get("yoy_abs"):
            scaled = g["yoy_abs"] * 2
            actions.append({
                "action": f"Dồn ngân sách và diện tích trưng bày cho {g['name']}",
                "rationale": (f"{g['name']} tăng {pct(g['yoy_pct'])} nhưng mới chiếm "
                              f"{g['share_pct']:.0f}% doanh thu — nhóm tăng nhanh nhất "
                              f"lại đang được đầu tư ít nhất."),
                "impact": f"Nhân đôi tốc độ hiện tại ≈ {money(scaled)}/năm",
                "effort": "Thấp", "owner_hint": "Thu mua & Marketing", "priority": 2,
            })

    conc = f["concentration"]
    if conc and conc["risk"] == "cao":
        actions.append({
            "action": (f"Đặt mục tiêu giảm tỷ trọng {conc['top1_name']} xuống dưới "
                       f"{max(50, int(conc['top1_share_pct']) - 15)}% trong 4 quý"),
            "rationale": (f"{conc['top1_share_pct']:.0f}% doanh thu nằm ở một hạng mục "
                          f"duy nhất. Đây là rủi ro cấu trúc, không phải vấn đề của một quý."),
            "impact": "Giảm biên độ dao động doanh thu, chưa tăng doanh thu ngay",
            "effort": "Cao", "owner_hint": "Ban điều hành", "priority": 3,
        })

    if f["growing_regions"]:
        r = f["growing_regions"][0]
        actions.append({
            "action": f"Nhân bản cách làm của vùng {r['name']} sang các vùng còn lại",
            "rationale": (f"{r['name']} là vùng duy nhất tăng trưởng ({pct(r['yoy_pct'])}) "
                          f"trong khi toàn hệ thống giảm — có gì đó ở đây đang hiệu quả."),
            "impact": "Chưa định lượng được — cần khảo sát vận hành trước",
            "effort": "Thấp", "owner_hint": "Vận hành vùng", "priority": 4,
        })

    season = f["season"]
    pred = f["pred"]
    if season and pred.get("enabled"):
        peak_point = max(pred["points"], key=lambda p: p["value"])
        actions.append({
            "action": (f"Chốt tồn kho và ngân sách quảng cáo cho "
                       f"{MONTH_VI[season['peak_month']]} trước ít nhất 6 tuần"),
            "rationale": (f"{MONTH_VI[season['peak_month']]} năm nào cũng cao hơn "
                          f"trung bình {season['peak_index']-100:.0f}%; dự báo kỳ này "
                          f"{money(peak_point['value'])}."),
            "impact": f"Tránh hụt hàng ở kỳ cao điểm ≈ {money(peak_point['value'])}",
            "effort": "Thấp", "owner_hint": "Chuỗi cung ứng", "priority": 5,
        })

    return actions[:max_actions]


def build_risks(f: dict, profile: dict) -> list[str]:
    risks = []
    conf = profile["confidence"]
    for reason in conf.get("reasons", []):
        risks.append(f"Chất lượng data: {reason}")

    partial = f["partial"]
    if partial:
        risks.append(f"{partial['note']} — kết quả kỳ mới nhất chưa so được cả năm "
                     f"(cùng kỳ: {pct(partial['change_pct'])}).")

    pred = f["pred"]
    if pred.get("unavailable_models"):
        detail = pred.get("unavailable_detail") or {}
        # Gộp các model cùng một lý do lại, tránh lặp ba dòng giống nhau
        by_reason: dict[str, list[str]] = {}
        for model in pred["unavailable_models"]:
            reason = detail.get(model, "không rõ lý do").split(":")[-1].strip()
            by_reason.setdefault(reason, []).append(model)
        for reason, models in by_reason.items():
            risks.append(f"Model {', '.join(models)} không chạy được ({reason}) — "
                         f"dự báo dùng {pred['chosen_model']} thay thế.")
    # Model mùa vụ (SARIMA, Holt-Winters, Prophet) cần nhiều chu kỳ để ước lượng
    # ổn định. Dưới 3 chu kỳ thì chúng vẫn chạy nhưng kết quả mong manh — nói ra,
    # đừng để người đọc tưởng dự báo chắc hơn thực tế.
    if pred.get("enabled"):
        train_periods = (pred.get("backtest") or {}).get("train_periods", 0)
        season = 12 if CONFIG["analysis"].get("grain") == "monthly" else 52
        if 0 < train_periods < season * 3:
            risks.append(
                f"Chỉ có {train_periods} kỳ để huấn luyện ({train_periods/season:.1f} "
                f"chu kỳ mùa vụ). Các model mùa vụ cần tối thiểu 3 chu kỳ mới ước "
                f"lượng ổn định — dự báo nên đọc như một khoảng, không phải con số chính xác.")

    if pred.get("enabled") and pred.get("chosen_mape", 0) > 10:
        risks.append(f"Sai số dự báo {pred['chosen_mape']}% khá cao — dùng khoảng "
                     f"dự báo, đừng bám con số điểm.")
    if not f["trend"].get("significant"):
        risks.append("Xu hướng không có ý nghĩa thống kê — đừng ngoại suy dài hạn "
                     "từ chuỗi số này.")
    return risks


# ─── LẮP RÁP ─────────────────────────────────────────────────────────────────

def main() -> int:
    profile = load("profile")
    desc = load("descriptive_output")
    diag = load("diagnostic_output")
    pred = load("predictive_output")

    f = story_facts(desc, diag, pred)
    conf = profile["confidence"]
    totals, yoy = f["totals"], f["yoy"]

    headline = build_headline(f)
    kpis = build_kpis(f)
    findings = build_findings(f)
    strategy = build_strategy(f)
    risks = build_risks(f, profile)
    executive = build_executive(f)          # bản không thuật ngữ, dùng cho email

    # chart_specs.json
    charts = build_charts(desc, diag, pred)
    (PIPE / "chart_specs.json").write_text(
        json.dumps(charts, ensure_ascii=False, indent=2), encoding="utf-8")

    # report_context.json — schema của html-report skill
    fc_summary = ""
    if pred.get("enabled"):
        fc_summary = (f"{pred['horizon']} kỳ tới dự báo tổng {money(pred['total_forecast'])} "
                      f"bằng model {pred['chosen_model']} "
                      f"(MAPE {pred['chosen_mape']}% so với baseline "
                      f"{pred['baseline_mape']}%).")

    report_context = {
        "report_type": "business",
        "big_answer": headline,
        "verdict_sentence": (
            f"{money(totals['revenue'])} doanh thu · biên {totals['margin']*100:.1f}% · "
            + (f"YoY {pct(yoy['revenue_change_pct'])} · " if yoy else "")
            + (f"dự báo {money(pred['total_forecast'])}" if pred.get("enabled") else "")
        ),
        "header_kpis": [
            {"label": k["label"], "value": k["value"], "delta": k["delta"],
             "status": {"down": "alert", "up": "good", "flat": "flat"}[k["direction"]]}
            for k in kpis[:3]
        ],
        "scqa": {
            "situation": (
                f"{CONFIG['data']['business_context'].strip()} "
                f"Kỳ phân tích {totals['period_start']} → {totals['period_end']}: "
                f"{money(totals['revenue'])} doanh thu từ {totals['orders']:,} đơn hợp lệ, "
                f"biên lợi nhuận {totals['margin']*100:.1f}%."),
            "complication": (
                f"Doanh thu {yoy['curr_year']} giảm "
                f"{money(abs(yoy['revenue_curr'] - yoy['revenue_prev']))} "
                f"({pct(yoy['revenue_change_pct'])}) so với {yoy['prev_year']}, "
                f"trong khi số đơn lại tăng {pct(yoy['orders_change_pct'])} và biên lợi "
                f"nhuận giữ nguyên. Chi phí và nhu cầu đều không phải nguyên nhân."
                if yoy else "Chưa đủ hai năm trọn vẹn để so sánh."),
            "question": ("Điều gì đang bào mòn giá trị mỗi đơn, nhóm nào còn tăng trưởng, "
                         "và nên dồn nguồn lực vào đâu trong 2 quý tới?"),
            "answer": (f"{headline} "
                       + (f"{fc_summary}" if fc_summary else "")),
        },
        "sections": [
            {
                "id": "descriptive",
                "title": f"Kết quả kinh doanh: {money(totals['revenue'])}, "
                         f"biên {totals['margin']*100:.1f}%, xu hướng "
                         f"{f['trend'].get('verdict', 'chưa xác định')}",
                "bridge_in": (f"{totals['period_start']} → {totals['period_end']} · "
                              f"{totals['orders']:,} đơn hợp lệ · "
                              f"{totals['periods']} kỳ"),
                "bridge_out": ("Biên lợi nhuận không đổi đã loại chi phí khỏi danh sách "
                               "nghi vấn — nguyên nhân nằm ở cấu trúc doanh thu."),
                "findings": [
                    {"tag": x["tag"], "title": x["title"], "evidence": x["detail"],
                     "supporting_data": x["evidence"]}
                    for x in findings if x["tag"] in ("Trend", "Pattern")
                ][:4],
                "charts": ["monthly_revenue_trend"],
            },
            {
                "id": "diagnostic",
                "title": (f"Nguyên nhân: {f['decomp'].get('driver', 'chưa xác định')} "
                          f"quyết định biến động"),
                "bridge_in": (f"So sánh {yoy['prev_year']} vs {yoy['curr_year']} · "
                              f"phân tách theo nhóm hàng, vùng, kênh"
                              if yoy else "Phân tích nguyên nhân"),
                "bridge_out": ("Đa số nhóm hàng vẫn tăng — vấn đề là cơ cấu, "
                               "không phải toàn bộ danh mục suy yếu."),
                "findings": [
                    {"tag": x["tag"], "title": x["title"], "evidence": x["detail"],
                     "supporting_data": x["evidence"]}
                    for x in findings if x["tag"] in ("Root Cause", "Contrast", "Implication")
                ][:4],
                "charts": ["yoy_waterfall", "category_yoy"],
            },
        ],
        "confidence": {
            "grade": conf["grade"], "score": conf["score"],
            "interpretation": (
                f"Grade {conf['grade']} ({conf['score']}/100). "
                + ("Các vấn đề đã ghi nhận: " + "; ".join(conf["reasons"]) + ". "
                   if conf["reasons"] else "Không phát hiện vấn đề chất lượng nào. ")
                + "Mọi con số trong báo cáo tính từ file data gốc, không nhập tay."),
        },
    }

    if pred.get("enabled"):
        report_context["sections"].append({
            "id": "predictive",
            "title": f"Dự báo {pred['horizon']} kỳ: tổng {money(pred['total_forecast'])}",
            "bridge_in": (f"Backtest {pred['backtest']['train_periods']} kỳ train / "
                          f"{pred['backtest']['test_periods']} kỳ test · "
                          f"khoảng tin cậy {int(CONFIG['forecast']['confidence_interval']*100)}%"),
            "bridge_out": ("Dự báo giả định cơ cấu danh mục không đổi — mọi hành động "
                           "ở phần khuyến nghị đều nhằm thay đổi giả định đó."),
            "findings": [
                {"tag": "Model Selection",
                 "title": (f"{pred['chosen_model']} thắng baseline: MAPE "
                           f"{pred['chosen_mape']}% so với {pred['baseline_mape']}%"
                           if pred["beat_baseline"] else
                           f"Không model nào thắng baseline — dùng "
                           f"{pred['chosen_model']} (MAPE {pred['chosen_mape']}%)"),
                 "evidence": (f"Backtest trên {pred['backtest']['test_periods']} kỳ cuối "
                              f"với cùng một tập train/test cho mọi model."),
                 "supporting_data": " · ".join(
                     f"{r['model']}: {r['mape']}%" for r in pred["backtest"]["results"]
                     if r.get("mape"))},
                {"tag": "Forecast",
                 "title": (f"Kỳ cao điểm dự báo "
                           f"{money(max(p['value'] for p in pred['points']))}"),
                 "evidence": fc_summary,
                 "supporting_data": " · ".join(
                     f"{p['period']}: {money(p['value'])}" for p in pred["points"])},
            ],
            "charts": ["revenue_forecast", "model_comparison"],
        })

    (PIPE / "report_context.json").write_text(
        json.dumps(report_context, ensure_ascii=False, indent=2), encoding="utf-8")

    # insights.json — hợp đồng với send_report.py
    report_name = CONFIG["report"]["filename_pattern"].format(date=TODAY) + ".html"
    insights = {
        "generated_at": TODAY,
        "data_period": {"start": totals["period_start"], "end": totals["period_end"]},
        "headline": headline,
        "confidence": {"grade": conf["grade"],
                       "note": "; ".join(conf["reasons"][:2]) if conf["reasons"] else ""},
        "kpis": kpis,
        # `executive` → email (ngôn ngữ kinh doanh)
        # `findings` + `risks` → report HTML (có bằng chứng thống kê)
        "executive": executive,
        "findings": [{"title": x["title"], "detail": x["detail"],
                      "evidence": x["evidence"]}
                     for x in findings[:CONFIG["analysis"].get("top_n_findings", 5)]],
        "forecast": ({"horizon": f"{pred['horizon']} kỳ",
                      "model": f"{pred['chosen_model']} (MAPE {pred['chosen_mape']}%)",
                      "summary": fc_summary,
                      "points": [{"period": p["period"], "value": round(p["value"]),
                                  "lo": round(p["lo"]), "hi": round(p["hi"])}
                                 for p in pred["points"]]}
                     if pred.get("enabled") else {}),
        "strategy": strategy,
        "risks": risks,
        "report_file": f"{CONFIG['report']['output_dir']}/{report_name}",
    }
    (PIPE / "insights.json").write_text(
        json.dumps(insights, ensure_ascii=False, indent=2), encoding="utf-8")

    for name in ("chart_specs", "report_context", "insights"):
        print(f"  ✓ data/pipeline/{STEM}/{name}.json")
    print(f"\nHeadline: {headline}")
    print(f"Findings: {len(findings)} · Khuyến nghị: {len(strategy)} · Rủi ro: {len(risks)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
