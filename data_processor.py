"""
Smart Data Cleaning & Preprocessing Engine
-------------------------------------------
Analyses, cleans, preprocesses tabular data and tracks every change.
"""

import io
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def analyse_dataframe(df: pd.DataFrame) -> dict:
    """Return a dict describing every quality issue in *df*."""
    issues = []
    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "issues": issues,
        "column_info": [],
    }

    # Column-level info
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isna().sum()),
            "missing_pct": round(df[col].isna().mean() * 100, 2),
            "unique": int(df[col].nunique()),
        }
        summary["column_info"].append(col_info)

    # --- Missing values ---
    for col in df.columns:
        n_miss = int(df[col].isna().sum())
        if n_miss > 0:
            issues.append({
                "type": "missing_values",
                "severity": "high" if df[col].isna().mean() > 0.3 else "medium",
                "column": col,
                "detail": f"{n_miss} missing ({df[col].isna().mean()*100:.1f}%)",
            })

    # --- Duplicate rows ---
    n_dup = int(df.duplicated().sum())
    if n_dup > 0:
        issues.append({
            "type": "duplicate_rows",
            "severity": "medium",
            "column": "(all)",
            "detail": f"{n_dup} duplicate rows",
        })

    # --- Constant / near-constant columns ---
    for col in df.columns:
        if df[col].nunique(dropna=True) <= 1:
            issues.append({
                "type": "constant_column",
                "severity": "low",
                "column": col,
                "detail": "Column has only one unique value",
            })

    # --- Outliers (IQR – numeric only) ---
    for col in df.select_dtypes(include="number").columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        n_outliers = int(((df[col] < lower) | (df[col] > upper)).sum())
        if n_outliers > 0:
            issues.append({
                "type": "outliers",
                "severity": "medium",
                "column": col,
                "detail": f"{n_outliers} outliers (IQR method)",
            })

    # --- Whitespace issues in text ---
    for col in df.select_dtypes(include="object").columns:
        has_leading_trailing = df[col].dropna().apply(lambda v: v != v.strip() if isinstance(v, str) else False)
        n = int(has_leading_trailing.sum())
        if n > 0:
            issues.append({
                "type": "whitespace",
                "severity": "low",
                "column": col,
                "detail": f"{n} values with leading/trailing whitespace",
            })

    return summary


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

def clean_dataframe(df: pd.DataFrame, options: dict) -> tuple[pd.DataFrame, list[dict]]:
    """
    Apply selected cleaning operations and return (cleaned_df, changes).

    *options* keys (all optional, default False):
        missing_strategy : 'mean' | 'median' | 'mode' | 'drop'
        remove_duplicates : bool
        remove_constant_cols : bool
        trim_whitespace : bool
        handle_outliers : 'cap' | 'remove' | None
    """
    df = df.copy()
    changes: list[dict] = []

    # 1. Trim whitespace
    if options.get("trim_whitespace"):
        for col in df.select_dtypes(include="object").columns:
            before_sample = df[col].dropna().head(3).tolist()
            trimmed = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
            n_changed = int((trimmed != df[col]).sum())
            if n_changed > 0:
                df[col] = trimmed
                changes.append({
                    "operation": "trim_whitespace",
                    "column": col,
                    "rows_affected": n_changed,
                    "before_sample": before_sample,
                    "after_sample": df[col].dropna().head(3).tolist(),
                })

    # 2. Remove duplicates
    if options.get("remove_duplicates"):
        n_before = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        n_removed = n_before - len(df)
        if n_removed > 0:
            changes.append({
                "operation": "remove_duplicates",
                "column": "(all)",
                "rows_affected": n_removed,
                "before_sample": [f"{n_before} rows"],
                "after_sample": [f"{len(df)} rows"],
            })

    # 3. Handle missing values
    strategy = options.get("missing_strategy")
    if strategy:
        for col in df.columns:
            n_miss = int(df[col].isna().sum())
            if n_miss == 0:
                continue

            before_sample = df[col].head(5).tolist()
            if strategy == "drop":
                df = df.dropna(subset=[col]).reset_index(drop=True)
            elif strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                fill_val = df[col].mean()
                df[col] = df[col].fillna(fill_val)
            elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
                fill_val = df[col].median()
                df[col] = df[col].fillna(fill_val)
            elif strategy == "mode":
                mode_vals = df[col].mode()
                if not mode_vals.empty:
                    df[col] = df[col].fillna(mode_vals.iloc[0])
            else:
                # Non-numeric with mean/median → fallback to mode
                mode_vals = df[col].mode()
                if not mode_vals.empty:
                    df[col] = df[col].fillna(mode_vals.iloc[0])

            changes.append({
                "operation": f"fill_missing ({strategy})",
                "column": col,
                "rows_affected": n_miss,
                "before_sample": before_sample,
                "after_sample": df[col].head(5).tolist(),
            })

    # 4. Handle outliers
    outlier_strategy = options.get("handle_outliers")
    if outlier_strategy:
        for col in df.select_dtypes(include="number").columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask = (df[col] < lower) | (df[col] > upper)
            n_outliers = int(mask.sum())
            if n_outliers == 0:
                continue

            before_sample = df.loc[mask, col].head(5).tolist()
            if outlier_strategy == "cap":
                df.loc[df[col] < lower, col] = lower
                df.loc[df[col] > upper, col] = upper
            elif outlier_strategy == "remove":
                df = df[~mask].reset_index(drop=True)

            changes.append({
                "operation": f"outliers ({outlier_strategy})",
                "column": col,
                "rows_affected": n_outliers,
                "before_sample": [str(v) for v in before_sample],
                "after_sample": df[col].head(5).tolist() if outlier_strategy == "remove" else df.loc[mask.head(5).index.intersection(df.index), col].tolist(),
            })

    # 5. Remove constant columns
    if options.get("remove_constant_cols"):
        const_cols = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]
        for col in const_cols:
            unique_val = df[col].dropna().unique().tolist()
            df = df.drop(columns=[col])
            changes.append({
                "operation": "remove_constant_column",
                "column": col,
                "rows_affected": 0,
                "before_sample": unique_val,
                "after_sample": ["(column removed)"],
            })

    return df, changes


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def preprocess_dataframe(df: pd.DataFrame, options: dict) -> tuple[pd.DataFrame, list[dict]]:
    """
    Apply preprocessing steps and return (processed_df, changes).

    *options* keys (all optional):
        encode_categorical : 'label' | 'onehot' | None
        scale_numeric : 'standard' | 'minmax' | None
        extract_datetime : bool
    """
    df = df.copy()
    changes: list[dict] = []

    # 1. Datetime feature extraction
    if options.get("extract_datetime"):
        for col in list(df.columns):
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                pass  # already datetime
            else:
                try:
                    converted = pd.to_datetime(df[col], errors="coerce")
                    if converted.notna().mean() > 0.5:
                        df[col] = converted
                    else:
                        continue
                except Exception:
                    continue

            if pd.api.types.is_datetime64_any_dtype(df[col]):
                base = col
                df[f"{base}_year"] = df[col].dt.year
                df[f"{base}_month"] = df[col].dt.month
                df[f"{base}_day"] = df[col].dt.day
                df[f"{base}_dayofweek"] = df[col].dt.dayofweek
                df = df.drop(columns=[col])
                changes.append({
                    "operation": "extract_datetime",
                    "column": base,
                    "rows_affected": len(df),
                    "before_sample": [base],
                    "after_sample": [f"{base}_year", f"{base}_month", f"{base}_day", f"{base}_dayofweek"],
                })

    # 2. Encode categoricals
    encode = options.get("encode_categorical")
    if encode:
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        for col in cat_cols:
            before_sample = df[col].head(5).tolist()
            n_unique = df[col].nunique()

            # Decide encoding strategy
            use_onehot = (encode == "onehot" and n_unique <= 15)
            use_label = (encode == "label") or (encode == "onehot" and n_unique > 15)

            if use_label:
                le = LabelEncoder()
                non_null_mask = df[col].notna()
                df.loc[non_null_mask, col] = le.fit_transform(df.loc[non_null_mask, col].astype(str))
                df[col] = pd.to_numeric(df[col], errors="coerce")
                op_name = "label_encode"
                if encode == "onehot" and n_unique > 15:
                    op_name = f"label_encode (auto — {n_unique} unique values too many for one-hot)"
                changes.append({
                    "operation": op_name,
                    "column": col,
                    "rows_affected": int(non_null_mask.sum()),
                    "before_sample": before_sample,
                    "after_sample": df[col].head(5).tolist(),
                })
            elif use_onehot:
                dummies = pd.get_dummies(df[col], prefix=col, dummy_na=False)
                df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
                changes.append({
                    "operation": "onehot_encode",
                    "column": col,
                    "rows_affected": len(df),
                    "before_sample": before_sample,
                    "after_sample": list(dummies.columns[:5]),
                })

    # 3. Scale numeric columns
    scale = options.get("scale_numeric")
    if scale:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            before_sample = {c: df[c].head(3).tolist() for c in num_cols[:5]}
            if scale == "standard":
                scaler = StandardScaler()
            else:
                scaler = MinMaxScaler()
            df[num_cols] = scaler.fit_transform(df[num_cols].fillna(0))
            after_sample = {c: df[c].head(3).tolist() for c in num_cols[:5]}
            changes.append({
                "operation": f"scale ({scale})",
                "column": ", ".join(num_cols[:5]) + ("..." if len(num_cols) > 5 else ""),
                "rows_affected": len(df),
                "before_sample": before_sample,
                "after_sample": after_sample,
            })

    return df, changes


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------

def read_file(file_storage, filename: str) -> pd.DataFrame:
    """Read an uploaded file into a DataFrame."""
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        return pd.read_csv(file_storage)
    elif ext in ("xls", "xlsx"):
        return pd.read_excel(file_storage, engine="openpyxl")
    elif ext == "json":
        return pd.read_json(file_storage)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def df_to_download_bytes(df: pd.DataFrame, fmt: str = "csv") -> io.BytesIO:
    """Serialize *df* to an in-memory bytes buffer."""
    buf = io.BytesIO()
    if fmt == "csv":
        df.to_csv(buf, index=False)
    elif fmt == "xlsx":
        df.to_excel(buf, index=False, engine="openpyxl")
    elif fmt == "json":
        buf.write(df.to_json(orient="records", indent=2).encode())
    buf.seek(0)
    return buf


def _safe_convert(v):
    """Convert a single value to a JSON-safe Python type."""
    try:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return None
    except (TypeError, ValueError):
        pass
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, (np.ndarray,)):
        return v.tolist()
    return v


def df_preview(df: pd.DataFrame, max_rows: int = 100) -> list[dict]:
    """Return a JSON-safe list-of-dicts preview of *df*."""
    preview_df = df.head(max_rows).copy()
    # Convert to native Python types to avoid JSON serialisation issues
    for col in preview_df.columns:
        preview_df[col] = preview_df[col].apply(_safe_convert)
    return preview_df.to_dict(orient="records")
