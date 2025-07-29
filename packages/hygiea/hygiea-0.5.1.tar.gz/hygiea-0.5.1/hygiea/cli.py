import argparse
import pandas as pd
import sys
from .utils import (
    standardize_column_names,
    load_config,
    save_log,
    read_sql_table,
    write_sql_table
)
from .cleaning import clean_data, generate_data_dictionary, encode_categoricals
from .eda import (
    generate_eda_report,
    class_balance_report,
    target_guided_eda,
    timeseries_profile,
    text_profile_summary
)
from .profiling import generate_html_profile

def main():
    parser = argparse.ArgumentParser(
        description="Hygiea: Clean, profile, and analyze data"
    )
    parser.add_argument(
        "--input", "-i", required=True, help="Path to input CSV (or 'db://conn_string:table' for SQL)."
    )
    parser.add_argument(
        "--output", "-o", required=True, help="Path for cleaned output CSV (or 'db://conn_string:table' to write to SQL)."
    )
    parser.add_argument(
        "--config", "-c", help="YAML/JSON pipeline config file (optional)."
    )
    parser.add_argument(
        "--report_dir", "-r", default="eda_report", help="Directory for standard EDA CSV outputs."
    )
    parser.add_argument(
        "--profile_html", "-p", help="Path to save interactive HTML profiling report (optional)."
    )
    parser.add_argument(
        "--generate_dict", "-d", action="store_true", help="Flag to generate data dictionary CSV."
    )
    parser.add_argument(
        "--target_column", "-t", help="Column name for target-guided EDA (optional)."
    )
    parser.add_argument(
        "--time_column", "-s", help="Column name for time-series profiling (optional)."
    )
    parser.add_argument(
        "--text_columns", "-x", nargs="+", help="List of text columns for text profiling (optional)."
    )
    args = parser.parse_args()

    log_lines = []
    # 1) Load data (CSV or SQL)
    if args.input.startswith("db://"):
        # Format: db://conn_string:table
        try:
            conn_str, table = args.input[5:].split(":", 1)
            df = read_sql_table(conn_str, table)
            log_lines.append(f"Loaded table '{table}' from '{conn_str}'.")
        except Exception as e:
            print(f"Error reading SQL table: {e}")
            sys.exit(1)
    else:
        try:
            df = pd.read_csv(args.input)
            log_lines.append(f"Loaded CSV '{args.input}'.")
        except Exception as e:
            print(f"Error reading CSV input: {e}")
            sys.exit(1)

    # 2) Standardize column names
    df = standardize_column_names(df)
    log_lines.append("Standardized column names.")

    # 3) Load pipeline config if provided
    if args.config:
        try:
            config = load_config(args.config)
            log_lines.append(f"Loaded config from '{args.config}'.")
            # Interpret config dictionary and override defaults as needed
            clean_params = config.get("clean_data", {})
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    else:
        clean_params = {}

    # 4) Clean data
    try:
        df_clean, sublogs = clean_data(df, **clean_params)
        log_lines.extend(sublogs)
        log_lines.append("Data cleaning completed.")
    except Exception as e:
        print(f"Error during cleaning: {e}")
        sys.exit(1)

    # 5) Encode categoricals (using defaults or config)
    one_hot_threshold = clean_params.get("one_hot_threshold", 10)
    try:
        df_clean = encode_categoricals(df_clean, one_hot_threshold=one_hot_threshold, target_column=args.target_column)
        log_lines.append("Categorical encoding completed.")
    except Exception as e:
        print(f"Error during categorical encoding: {e}")
        sys.exit(1)

    # 6) Save cleaned data (CSV or SQL)
    if args.output.startswith("db://"):
        try:
            conn_str, table = args.output[5:].split(":", 1)
            write_sql_table(df_clean, conn_str, table)
            log_lines.append(f"Saved cleaned data to table '{table}' in '{conn_str}'.")
        except Exception as e:
            print(f"Error writing to SQL: {e}")
            sys.exit(1)
    else:
        try:
            df_clean.to_csv(args.output, index=False)
            log_lines.append(f"Saved cleaned CSV to '{args.output}'.")
        except Exception as e:
            print(f"Error saving cleaned CSV: {e}")
            sys.exit(1)

    # 7) Generate data dictionary if requested
    if args.generate_dict:
        try:
            dd = generate_data_dictionary(df_clean, output_path=os.path.join(args.report_dir, "data_dictionary.csv"))
            log_lines.append("Data dictionary generated.")
        except Exception as e:
            print(f"Error generating data dictionary: {e}")
            sys.exit(1)

    # 8) Standard EDA CSVs
    try:
        generate_eda_report(df_clean, output_dir=args.report_dir)
        log_lines.append(f"Standard EDA CSVs saved to '{args.report_dir}'.")
    except Exception as e:
        print(f"Error generating EDA report: {e}")
        sys.exit(1)

    # 9) Class balance (if target provided)
    if args.target_column:
        try:
            class_balance_report(df_clean, args.target_column, output_path=os.path.join(args.report_dir, "class_balance.csv"))
            log_lines.append("Class balance report generated.")
        except Exception as e:
            print(f"Error in class balance report: {e}")

        # Target-guided EDA
        try:
            target_guided_eda(df_clean, args.target_column, output_dir=os.path.join(args.report_dir, "target_eda"))
            log_lines.append("Target-guided EDA completed.")
        except Exception as e:
            print(f"Error generating target-guided EDA: {e}")

    # 10) Time-series profiling (if provided)
    if args.time_column:
        try:
            timeseries_profile(df_clean, args.time_column, output_dir=os.path.join(args.report_dir, "timeseries_eda"))
            log_lines.append("Time-series profiling completed.")
        except Exception as e:
            print(f"Error in time-series profiling: {e}")

    # 11) Text profiling (if provided)
    if args.text_columns:
        try:
            text_profile_summary(df_clean, args.text_columns, output_dir=os.path.join(args.report_dir, "text_profile"))
            log_lines.append("Text profiling completed.")
        except Exception as e:
            print(f"Error in text profiling: {e}")

    # 12) HTML profile (if requested)
    if args.profile_html:
        try:
            generate_html_profile(df_clean, output_html=args.profile_html)
            log_lines.append(f"Interactive HTML profile saved to '{args.profile_html}'.")
        except Exception as e:
            print(f"Error generating HTML profiling report: {e}")

    # 13) Save logs
    log_path = save_log(log_lines)
    print(f"Hygiea pipeline completed. Logs saved to: {log_path}")

if __name__ == "__main__":
    import os
    main()
