import pandas as pd
from pandas_profiling import ProfileReport

def generate_html_profile(df: pd.DataFrame, output_html="profile.html", minimal=False):
    """
    Generate an interactive HTML profiling report using pandas_profiling.
    If minimal=True, skip expensive computations (like correlations).
    """
    profile = ProfileReport(
        df,
        title="Hygiea Data Profile",
        minimal=minimal,
        explorative=True
    )
    profile.to_file(output_html)
    return output_html
