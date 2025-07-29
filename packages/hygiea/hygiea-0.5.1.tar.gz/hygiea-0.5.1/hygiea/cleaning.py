import pandas as pd
import numpy as np

# Enable the experimental IterativeImputer API before importing
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import KNNImputer, IterativeImputer

from sklearn.preprocessing import LabelEncoder
from scipy.stats import zscore

def drop_high_missing_columns(df: pd.DataFrame, threshold: float = 0.8) -> pd.DataFrame:
    missing_pct = df.isnull().mean()
    cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
    return df.drop(columns=cols_to_drop)

def drop_high_missing_rows(df: pd.DataFrame, threshold: float = 0.8) -> pd.DataFrame:
    row_missing_pct = df.isnull().mean(axis=1)
    return df.loc[row_missing_pct <= threshold].reset_index(drop=True)

def detect_low_variance(df: pd.DataFrame, variance_threshold: float = 0.0) -> list:
    variances = df.select_dtypes(include=[np.number]).var()
    low_var_cols = variances[variances <= variance_threshold].index.tolist()
    return low_var_cols

def automatic_type_conversion(df: pd.DataFrame, log_lines: list = None) -> pd.DataFrame:
    df_conv = df.copy()
    if log_lines is None:
        log_lines = []

    for col in df_conv.columns:
        series = df_conv[col]
        # Try datetime
        try:
            df_conv[col] = pd.to_datetime(series, errors="raise")
            log_lines.append(f"Column '{col}' converted to datetime.")
            continue
        except Exception:
            pass
        # Try numeric
        try:
            df_conv[col] = pd.to_numeric(series.str.replace(",", ""), errors="raise")
            log_lines.append(f"Column '{col}' converted to numeric.")
            continue
        except Exception:
            pass
        # Try boolean
        lower_vals = series.dropna().astype(str).str.lower().unique()
        if set(lower_vals).issubset({"true", "false", "yes", "no", "0", "1"}):
            df_conv[col] = series.astype(str).str.lower().map(
                {"true": True, "false": False, "yes": True, "no": False, "0": False, "1": True}
            )
            log_lines.append(f"Column '{col}' converted to boolean.")
            continue
    return df_conv

def clean_data(
    df: pd.DataFrame,
    drop_duplicates: bool = True,
    fill_missing_strategy: str = "median_mode",
    outlier_method: str = "IQR",
    missing_threshold: float = 0.8,
    knn_impute_cols: list = None,
    iterative_impute_cols: list = None,
    log_lines: list = None
) -> pd.DataFrame:
    df_work = df.copy()
    if log_lines is None:
        log_lines = []

    # 1) Drop duplicates
    if drop_duplicates:
        before = len(df_work)
        df_work = df_work.drop_duplicates().reset_index(drop=True)
        dropped = before - len(df_work)
        log_lines.append(f"Dropped {dropped} duplicate rows.")

    # 2) Automatic type conversion
    df_work = automatic_type_conversion(df_work, log_lines=log_lines)

    # 3) Drop high-missingness columns & rows
    df_work = drop_high_missing_columns(df_work, threshold=missing_threshold)
    df_work = drop_high_missing_rows(df_work, threshold=missing_threshold)
    log_lines.append("Dropped high-missingness columns/rows.")

    # 4) Fill missing values
    if fill_missing_strategy == "median_mode":
        for col in df_work.columns:
            if df_work[col].dtype in [np.float64, np.int64]:
                median = df_work[col].median()
                df_work[col] = df_work[col].fillna(median)
                log_lines.append(f"Filled missing in '{col}' with median={median}.")
            else:
                mode = df_work[col].mode()
                if not mode.empty:
                    df_work[col] = df_work[col].fillna(mode[0])
                    log_lines.append(f"Filled missing in '{col}' with mode='{mode[0]}'.")
                else:
                    df_work[col] = df_work[col].fillna("")
                    log_lines.append(f"Filled missing in '{col}' with empty string.")
    elif fill_missing_strategy == "knn":
        if knn_impute_cols is None:
            num_cols = df_work.select_dtypes(include=[np.number]).columns.tolist()
        else:
            num_cols = knn_impute_cols
        imputer = KNNImputer()
        df_work[num_cols] = imputer.fit_transform(df_work[num_cols])
        log_lines.append(f"KNN-imputed columns: {num_cols}.")
    elif fill_missing_strategy == "iterative":
        if iterative_impute_cols is None:
            num_cols = df_work.select_dtypes(include=[np.number]).columns.tolist()
        else:
            num_cols = iterative_impute_cols
        imputer = IterativeImputer(random_state=0)
        df_work[num_cols] = imputer.fit_transform(df_work[num_cols])
        log_lines.append(f"Iterative-imputed columns: {num_cols}.")

    # 5) Cap outliers
    if outlier_method == "IQR":
        for col in df_work.select_dtypes(include=[np.number]).columns:
            Q1 = df_work[col].quantile(0.25)
            Q3 = df_work[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df_work[col] = np.where(
                df_work[col] < lower, lower,
                np.where(df_work[col] > upper, upper, df_work[col])
            )
        log_lines.append("Outliers capped via IQR method.")
    elif outlier_method == "zscore":
        for col in df_work.select_dtypes(include=[np.number]).columns:
            zs = zscore(df_work[col].fillna(df_work[col].median()))
            df_work[col] = np.where(
                zs > 3, df_work[col].median() + 3 * df_work[col].std(),
                np.where(zs < -3, df_work[col].median() - 3 * df_work[col].std(), df_work[col])
            )
        log_lines.append("Outliers capped via z-score method.")

    # 6) Drop low-variance columns
    low_var = detect_low_variance(df_work, variance_threshold=0.0)
    if low_var:
        df_work = df_work.drop(columns=low_var)
        log_lines.append(f"Dropped low-variance columns: {low_var}.")

    return df_work, log_lines

def encode_categoricals(
    df: pd.DataFrame,
    one_hot_threshold: int = 10,
    target_column: str = None
) -> pd.DataFrame:
    df_enc = df.copy()
    cat_cols = df_enc.select_dtypes(include=["object", "category"]).columns.tolist()
    if not cat_cols:
        return df_enc

    for col in cat_cols:
        cardinality = df_enc[col].nunique()
        if cardinality <= one_hot_threshold:
            dummies = pd.get_dummies(df_enc[col], prefix=col)
            df_enc = pd.concat([df_enc.drop(columns=[col]), dummies], axis=1)
        else:
            if target_column and target_column in df_enc.columns:
                means = df_enc.groupby(col)[target_column].mean()
                df_enc[col + "_enc"] = df_enc[col].map(means)
                df_enc = df_enc.drop(columns=[col])
            else:
                le = LabelEncoder()
                df_enc[col] = le.fit_transform(df_enc[col].astype(str))
    return df_enc

def generate_data_dictionary(df: pd.DataFrame, output_path: str = "data_dictionary.csv"):
    rows = []
    total = len(df)
    for col in df.columns:
        dtype = str(df[col].dtype)
        nunique = df[col].nunique(dropna=True)
        samples = df[col].dropna().unique()[:5].tolist()
        missing_count = df[col].isnull().sum()
        missing_pct = missing_count / total * 100
        rows.append({
            "column": col,
            "dtype": dtype,
            "nunique": nunique,
            "sample_values": samples,
            "missing_count": int(missing_count),
            "missing_percent": round(missing_pct, 2)
        })
    dd = pd.DataFrame(rows)
    dd.to_csv(output_path, index=False)
    return dd
