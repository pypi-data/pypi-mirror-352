# Hygiea

**Hygiea** is a comprehensive Python package for data “hygiene”: automated cleaning, profiling, and basic feature engineering.  
It supports both Jupyter notebooks and command‑line usage.

## Key Features

1. **Column‑Name Standardization**  
   - Lowercase, replace spaces/special chars, optional mapping from user.

2. **Automatic Type Conversion**  
   - Detects and converts dates, numerics, booleans.

3. **Drop High‑Missingness**  
   - Drop columns/rows exceeding a missing‐value threshold.

4. **Low‑Variance / Constant Feature Detection**  
   - Identifies columns with near‑zero variance.

5. **Outlier Detection & Winsorization**  
   - IQR, Z‑score, or Isolation Forest.

6. **Categorical Encoding Suggestions & Utilities**  
   - Reports cardinality, frequency distribution, one‑hot/label/target encoding helpers.

7. **Multiple Imputation Strategies**  
   - Median/mode, KNN, MICE, forward/backward fill.

8. **Automated Visual Profiling**  
   - Generates an interactive HTML report (via `pandas_profiling`).

9. **Standard EDA Reports**  
   - Summary statistics, missingness CSV, correlation matrix, VIF, class imbalance.

10. **Target‑Guided EDA**  
    - If a target column is provided, outputs per‑class distributions and statistical tests.

11. **Time Series Profiling**  
    - Automatically detects datetime, outputs time‑series plots and rolling summaries.

12. **Text Cleaning & Tokenization Utilities**  
    - Lowercase, strip, remove punctuation, stopwords removal, optional stemming/lemmatization.

13. **Pipeline Configuration (YAML/JSON)**  
    - Define cleaning steps in a config file, with logging.

14. **Database & Big‑Data Support**  
    - Read/write from SQL, chunked CSV processing.

15. **Feature Engineering Helpers**  
    - Date feature extraction, interaction/polynomial features, binning.

16. **Quality & Consistency Checks**  
    - Unique ID validation, cross‑column logic rules, data‐drift detection.

17. **Model‑Ready Exports**  
    - Train/test split helper, `sklearn`‐compatible transformer, export feature metadata.

18. **Plugin/Extension System**  
    - Register custom cleaning/EDA rules via entry points.

---

## Installation

```bash
pip install hygiea
