import pandas as pd
import os
import numpy as np
from scipy.stats import chi2_contingency

# VIF requires statsmodels
try:
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    _HAS_STATS_MODELS = True
except ImportError:
    _HAS_STATS_MODELS = False

def generate_eda_report(df: pd.DataFrame, output_dir="eda_report"):
    """
    Generate standard EDA reports (CSV files) in output_dir:
      - summary_statistics.csv      (df.describe(include='all').transpose())
      - missing_values.csv          (col, missing_count, missing_percent)
      - correlation_matrix.csv      (for numeric cols)
      - vif.csv                     (Variance Inflation Factor for numeric cols, if available)
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1) Summary statistics
    summary = df.describe(include="all").transpose()
    summary.to_csv(os.path.join(output_dir, "summary_statistics.csv"))

    # 2) Missing values
    missing = df.isnull().sum().reset_index()
    missing.columns = ["column", "missing_count"]
    missing["missing_percent"] = missing["missing_count"] / len(df) * 100
    missing.to_csv(os.path.join(output_dir, "missing_values.csv"), index=False)

    # 3) Correlation matrix (numeric only)
    corr = df.corr()
    corr.to_csv(os.path.join(output_dir, "correlation_matrix.csv"))

    # 4) VIF (if statsmodels is installed)
    if _HAS_STATS_MODELS:
        num_df = df.select_dtypes(include=[np.number]).dropna()
        vif_data = []
        for i, col in enumerate(num_df.columns):
            vif = variance_inflation_factor(num_df.values, i)
            vif_data.append({"column": col, "VIF": vif})
        pd.DataFrame(vif_data).to_csv(os.path.join(output_dir, "vif.csv"), index=False)
    else:
        # If statsmodels is missing, create an empty file or skip
        with open(os.path.join(output_dir, "vif.csv"), "w") as f:
            f.write("VIF not computed (statsmodels not installed)\n")

def compute_vif(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Variance Inflation Factor for each numeric column.
    Returns a DataFrame with columns: ['column', 'VIF'].
    Requires statsmodels.
    """
    if not _HAS_STATS_MODELS:
        raise ImportError("statsmodels is required for compute_vif")
    num_df = df.select_dtypes(include=[np.number]).dropna()
    vif_data = []
    for i, col in enumerate(num_df.columns):
        vif = variance_inflation_factor(num_df.values, i)
        vif_data.append({"column": col, "VIF": vif})
    return pd.DataFrame(vif_data)

def class_balance_report(df: pd.DataFrame, target_column: str, output_path="class_balance.csv"):
    """
    Save class distribution for a classification target.
    """
    if target_column not in df.columns:
        raise KeyError(f"Target column '{target_column}' not found in DataFrame.")
    dist = df[target_column].value_counts(dropna=False).reset_index()
    dist.columns = [target_column, "count"]
    dist["percent"] = dist["count"] / len(df) * 100
    dist.to_csv(output_path, index=False)
    return dist

def target_guided_eda(df: pd.DataFrame, target_column: str, output_dir="target_eda"):
    """
    For each numeric/categorical column, produce:
      - Numeric: summary stats (mean, median, std, min, max) per class
      - Categorical: chi-square test vs. target and frequency per class
    Saves:
      - target_numeric_summary.csv
      - target_categorical_summary.csv
    """
    if target_column not in df.columns:
        raise KeyError(f"Target column '{target_column}' not found.")

    os.makedirs(output_dir, exist_ok=True)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.drop(target_column, errors="ignore")
    cat_cols = df.select_dtypes(include=["object", "category"]).columns

    # Numeric summary per class
    num_rows = []
    for col in numeric_cols:
        grp = df.groupby(target_column)[col]
        for cls, series in grp:
            row = {
                "column": col,
                "class": cls,
                "mean": series.mean(),
                "median": series.median(),
                "std": series.std(),
                "min": series.min(),
                "max": series.max()
            }
            num_rows.append(row)
    pd.DataFrame(num_rows).to_csv(os.path.join(output_dir, "target_numeric_summary.csv"), index=False)

    # Categorical summary per class + chi-square
    cat_rows = []
    for col in cat_cols:
        contingency = pd.crosstab(df[col], df[target_column])
        try:
            chi2, p, dof, _ = chi2_contingency(contingency)
        except:
            chi2, p = np.nan, np.nan
        for val in df[col].unique():
            for cls in df[target_column].unique():
                count = contingency.loc[val, cls] if val in contingency.index and cls in contingency.columns else 0
                cat_rows.append({
                    "column": col,
                    "value": val,
                    "class": cls,
                    "count": count,
                    "chi2_stat": chi2,
                    "p_value": p
                })
    pd.DataFrame(cat_rows).to_csv(os.path.join(output_dir, "target_categorical_summary.csv"), index=False)

def timeseries_profile(df: pd.DataFrame, time_column: str, output_dir="timeseries_eda"):
    """
    If time_column exists, produce:
      - record counts per day
      - missing date ranges
      - 7-day rolling mean/median for numeric features
    Saves:
      - ts_record_counts.csv
      - ts_missing_dates.csv
      - {col}_rolling_stats.csv for each numeric column
    """
    if time_column not in df.columns:
        raise KeyError(f"Time column '{time_column}' not found.")
    os.makedirs(output_dir, exist_ok=True)

    ts = pd.to_datetime(df[time_column], errors="coerce")
    df_ts = df.copy()
    df_ts[time_column] = ts

    # 1) Record counts per day
    counts = df_ts.set_index(time_column).resample("D").size().reset_index(name="count")
    counts.to_csv(os.path.join(output_dir, "ts_record_counts.csv"), index=False)

    # 2) Missing dates
    all_dates = pd.date_range(counts[time_column].min(), counts[time_column].max(), freq="D")
    missing_dates = all_dates.difference(counts[time_column])
    pd.DataFrame({"missing_date": missing_dates}).to_csv(os.path.join(output_dir, "ts_missing_dates.csv"), index=False)

    # 3) Rolling stats (7-day window) for numeric columns
    numeric_cols = df_ts.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        roll = df_ts.set_index(time_column)[col].rolling(window=7, min_periods=1)
        df_roll = pd.DataFrame({
            "date": roll.mean().index,
            f"{col}_rolling_mean": roll.mean().values,
            f"{col}_rolling_median": roll.median().values
        })
        df_roll.to_csv(os.path.join(output_dir, f"{col}_rolling_stats.csv"), index=False)

def text_profile_summary(df: pd.DataFrame, text_columns: list, output_dir="text_profile"):
    """
    For each text column, produce:
      - unique count
      - average length
      - top 20 most common tokens (after simple cleaning)
    Saves:
      - text_summary.csv
      - top_tokens_{col}.csv for each column
    """
    import nltk
    from nltk.corpus import stopwords
    from collections import Counter

    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)

    os.makedirs(output_dir, exist_ok=True)
    rows = []
    stop_words = set(stopwords.words("english"))

    for col in text_columns:
        series = df[col].astype(str).dropna()
        unique_count = series.nunique()
        avg_len = series.str.len().mean()

        # Tokenize, remove punctuation/stopwords
        tokens = []
        for text in series:
            toks = nltk.word_tokenize(text.lower())
            toks = [tok for tok in toks if tok.isalpha() and tok not in stop_words]
            tokens.extend(toks)
        freq = Counter(tokens).most_common(20)

        rows.append({
            "column": col,
            "unique_count": unique_count,
            "avg_length": avg_len
        })

        # Save top tokens table
        pd.DataFrame(freq, columns=["token", "count"]).to_csv(
            os.path.join(output_dir, f"top_tokens_{col}.csv"), index=False
        )

    pd.DataFrame(rows).to_csv(os.path.join(output_dir, "text_summary.csv"), index=False)
