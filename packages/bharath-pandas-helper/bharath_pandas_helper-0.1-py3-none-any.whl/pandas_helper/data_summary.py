import pandas as pd

def summarize_dataset(file_path):
    """
    Summarizes a CSV or Excel dataset with:
    - Basic Info
    - Null & Missing Info
    - Data Type Summary
    - Unique Values
    - Memory Usage
    - Numeric Column Analysis
    - Outlier Detection
    - Correlation Matrix
    - Categorical Summary
    """

    # ----------------------------
    # Load Dataset
    # ----------------------------
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format! Use CSV or Excel.")

    summary = {}

    # ----------------------------
    # 1. Basic Info
    # ----------------------------
    summary['basic_info'] = {
        'shape': df.shape,
        'columns': list(df.columns),
        'head': df.head().to_dict(orient='records')
    }

    # ----------------------------
    # 2. Null & Missing Info
    # ----------------------------
    null_counts = df.isnull().sum()
    summary['null_info'] = {
        'null_counts': null_counts.to_dict(),
        'missing_percentage': (null_counts / len(df) * 100).round(2).to_dict()
    }

    # ----------------------------
    # 3. Data Type Summary
    # ----------------------------
    summary['dtypes_info'] = {
        'column_dtypes': df.dtypes.apply(lambda x: x.name).to_dict(),
        'dtype_counts': df.dtypes.value_counts().to_dict()
    }

    # ----------------------------
    # 4. Unique Values
    # ----------------------------
    summary['unique_values'] = df.nunique().to_dict()

    # ----------------------------
    # 5. Memory Usage
    # ----------------------------
    summary['memory_usage_MB'] = round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2)

    # ----------------------------
    # 6. Numeric Column Analysis
    # ----------------------------
    numeric_df = df.select_dtypes(include='number')

    if not numeric_df.empty:
        # Aggregates
        summary['numeric_analysis'] = {
            'aggregates': numeric_df.agg(['mean', 'median', 'min', 'max', 'std']).round(2).to_dict()
        }

        # Outliers using IQR
        outliers = {}
        for col in numeric_df.columns:
            Q1 = numeric_df[col].quantile(0.25)
            Q3 = numeric_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outlier_count = ((numeric_df[col] < lower) | (numeric_df[col] > upper)).sum()
            outliers[col] = int(outlier_count)

        summary['numeric_analysis']['outliers'] = outliers

        # Correlation matrix
        summary['numeric_analysis']['correlation_matrix'] = numeric_df.corr(numeric_only=True).round(2).to_dict()
    else:
        summary['numeric_analysis'] = {
            'aggregates': {},
            'outliers': {},
            'correlation_matrix': {}
        }

    # ----------------------------
    # 7. Categorical Column Summary
    # ----------------------------
    cat_df = df.select_dtypes(include='object')
    categorical_summary = {}

    for col in cat_df.columns:
        value_counts = cat_df[col].value_counts()
        categorical_summary[col] = {
            'unique_count': int(value_counts.count()),
            'most_frequent': value_counts.index[0] if not value_counts.empty else None,
            'top_3_values': value_counts.head(3).to_dict()
        }

    summary['categorical_summary'] = categorical_summary

    return summary
