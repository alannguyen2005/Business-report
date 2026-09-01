# cleaning_helpers.py — Common data cleaning utilities
# Used by data-prep skill

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))  # reach ai_analyst/
from helpers.utils.logger import get_logger

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

_log = get_logger(__name__)


def detect_duplicates(df: pd.DataFrame) -> Dict:
    """Detect exact and near-duplicate rows."""
    exact = df.duplicated().sum()
    return {
        "exact_duplicates": int(exact),
        "pct_of_total": round(exact / len(df) * 100, 2) if len(df) > 0 else 0
    }


def fix_types(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
    """Auto-detect and fix column types."""
    log = []
    for col in df.columns:
        if df[col].dtype == object:
            # Try numeric
            try:
                converted = pd.to_numeric(df[col].str.replace(",", ""), errors="coerce")
                if converted.notna().mean() > 0.8:
                    df[col] = converted
                    log.append({"column": col, "from": "object", "to": "numeric"})
                    continue
            except (AttributeError, TypeError) as e:
                _log.debug("convert_failed", col=col, error=str(e))
            # Try datetime
            try:
                converted = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
                if converted.notna().mean() > 0.8:
                    df[col] = converted
                    log.append({"column": col, "from": "object", "to": "datetime"})
                    continue
            except (ValueError, TypeError) as e:
                _log.debug("convert_failed", col=col, error=str(e))
            # Clean strings
            df[col] = df[col].astype(str).str.strip()
    return df, log


def handle_missing(df: pd.DataFrame, strategy: str = "auto") -> Tuple[pd.DataFrame, List[Dict]]:
    """Handle missing values with appropriate strategy per column type."""
    log = []
    for col in df.columns:
        null_pct = df[col].isnull().mean() * 100
        if null_pct == 0:
            continue
        if null_pct > 50:
            log.append({"column": col, "action": "flagged_high_null", "pct": round(null_pct, 1)})
            continue  # Don't auto-fill if >50% missing
        if pd.api.types.is_numeric_dtype(df[col]):
            fill_val = df[col].median()
            df[col] = df[col].fillna(fill_val)
            log.append({"column": col, "action": "fill_median", "value": float(fill_val), "pct": round(null_pct, 1)})
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].interpolate(method="time")
            log.append({"column": col, "action": "interpolate_time", "pct": round(null_pct, 1)})
        else:
            fill_val = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "Unknown"
            df[col] = df[col].fillna(fill_val)
            log.append({"column": col, "action": "fill_mode", "value": str(fill_val), "pct": round(null_pct, 1)})
    return df, log


def detect_outliers_iqr(df: pd.DataFrame, columns: Optional[List[str]] = None) -> List[Dict]:
    """Detect outliers using IQR method. Flag but do NOT remove."""
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    outliers = []
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        count = mask.sum()
        if count > 0:
            outliers.append({
                "column": col,
                "count": int(count),
                "pct": round(count / len(df) * 100, 2),
                "lower_bound": float(lower),
                "upper_bound": float(upper)
            })
    return outliers


def profile_column(series: pd.Series) -> Dict:
    """Generate profile for a single column."""
    profile = {
        "name": series.name,
        "dtype": str(series.dtype),
        "null_count": int(series.isnull().sum()),
        "null_pct": round(series.isnull().mean() * 100, 2),
        "unique_count": int(series.nunique()),
    }
    if pd.api.types.is_numeric_dtype(series):
        profile.update({
            "mean": float(series.mean()) if not series.empty else None,
            "median": float(series.median()) if not series.empty else None,
            "std": float(series.std()) if not series.empty else None,
            "min": float(series.min()) if not series.empty else None,
            "max": float(series.max()) if not series.empty else None,
            "skew": float(series.skew()) if not series.empty else None,
        })
    elif pd.api.types.is_categorical_dtype(series) or series.dtype == object:
        vc = series.value_counts().head(10)
        profile["top_values"] = {str(k): int(v) for k, v in vc.items()}
    return profile
