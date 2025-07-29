import re
import yaml
import json
import os
import pandas as pd

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lowercase column names, replace spaces/special chars with underscores.
    """
    new_cols = []
    for col in df.columns:
        col_std = col.strip().lower()
        col_std = re.sub(r"[^\w]+", "_", col_std)
        col_std = re.sub(r"_+", "_", col_std).strip("_")
        new_cols.append(col_std)
    df.columns = new_cols
    return df

def load_config(config_path: str) -> dict:
    """
    Load YAML or JSON configuration for pipeline steps.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    ext = os.path.splitext(config_path)[1].lower()
    with open(config_path, "r", encoding="utf-8") as f:
        if ext in [".yml", ".yaml"]:
            return yaml.safe_load(f)
        elif ext == ".json":
            return json.load(f)
        else:
            raise ValueError("Config file must be .yml/.yaml or .json")

def save_log(log_lines: list, log_dir="hygiea_logs"):
    """
    Save a list of log lines (strings) to a timestamped .log file.
    """
    os.makedirs(log_dir, exist_ok=True)
    import datetime
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = os.path.join(log_dir, f"log_{ts}.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        for line in log_lines:
            f.write(line + "\n")
    return log_path

def read_sql_table(conn_string: str, table_name: str) -> pd.DataFrame:
    """
    Read a SQL table into a DataFrame using SQLAlchemy.
    """
    from sqlalchemy import create_engine
    engine = create_engine(conn_string)
    return pd.read_sql_table(table_name, con=engine)

def write_sql_table(df, conn_string: str, table_name: str, if_exists="replace"):
    """
    Write DataFrame to a SQL table.
    """
    from sqlalchemy import create_engine
    engine = create_engine(conn_string)
    df.to_sql(table_name, con=engine, if_exists=if_exists, index=False)
