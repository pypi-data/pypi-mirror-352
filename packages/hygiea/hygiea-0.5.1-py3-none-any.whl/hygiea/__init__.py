"""
Hygiea: Comprehensive Data Cleaning, Profiling, and EDA toolkit.

Usage (import-level):
    from hygiea.utils import standardize_column_names, load_config
    from hygiea.cleaning import clean_data, drop_high_missing
    from hygiea.eda import generate_eda_report, compute_vif
    from hygiea.profiling import generate_html_profile
    from hygiea import cli
"""
from .utils import standardize_column_names, load_config
from .cleaning import (
    clean_data,
    drop_high_missing_columns,
    drop_high_missing_rows,
    detect_low_variance,
    automatic_type_conversion,
    encode_categoricals,
    generate_data_dictionary,
)
from .eda import (
    generate_eda_report,
    compute_vif,
    class_balance_report,
    target_guided_eda,
    timeseries_profile,
    text_profile_summary,
)
from .profiling import generate_html_profile
