import pandas as pd

def load_and_describe(url: str) -> pd.DataFrame:
    """Load a CSV from a URL and print basic statistics."""
    df = pd.read_csv(url)
    print("\nBasic Statistics:")
    print(df.describe(include='all'))
    return df

def missing_report(df: pd.DataFrame):
    """Show missing value counts and percentages per column."""
    total = df.isnull().sum()
    percent = (total / len(df)) * 100
    report = pd.DataFrame({'missing_count': total, 'missing_percent': percent})
    print("\nMissing Value Report:")
    print(report)

def info_summary(df: pd.DataFrame):
    """Print DataFrame shape, column types, and memory usage."""
    print(f"\nShape: {df.shape}")
    print("\nColumn Types:")
    print(df.dtypes)
    print("\nMemory Usage:")
    print(df.memory_usage(deep=True)) 

def clean_data(df: pd.DataFrame, strategies: dict = None) -> pd.DataFrame:
    """Perform basic data cleaning operations.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to clean
    strategies : dict, optional
        Dictionary mapping column names to cleaning strategies.
        Available strategies: 'drop', 'mean', 'median', 'mode', 'zero', 'value:X'
        Example: {'age': 'median', 'name': 'drop', 'salary': 'value:0'}
    
    Returns:
    --------
    pandas.DataFrame
        Cleaned DataFrame
    """
    result = df.copy()
    
    # If no strategies provided, use default (drop rows with any NaN)
    if strategies is None:
        return result.dropna()
    
    # Apply cleaning strategies by column
    for col, strategy in strategies.items():
        if col not in result.columns:
            print(f"Warning: Column '{col}' not found in DataFrame")
            continue
            
        if strategy == 'drop':
            # Drop rows where this column has NaN
            result = result.dropna(subset=[col])
        elif strategy == 'mean' and pd.api.types.is_numeric_dtype(result[col]):
            # Fill NaN with mean for numeric columns
            result[col] = result[col].fillna(result[col].mean())
        elif strategy == 'median' and pd.api.types.is_numeric_dtype(result[col]):
            # Fill NaN with median for numeric columns
            result[col] = result[col].fillna(result[col].median())
        elif strategy == 'mode':
            # Fill NaN with mode (most frequent value)
            result[col] = result[col].fillna(result[col].mode()[0])
        elif strategy == 'zero' and pd.api.types.is_numeric_dtype(result[col]):
            # Fill NaN with zero for numeric columns
            result[col] = result[col].fillna(0)
        elif strategy.startswith('value:'):
            # Fill NaN with specific value
            fill_value = strategy.split(':', 1)[1]
            # Convert value to appropriate type if possible
            if pd.api.types.is_numeric_dtype(result[col]):
                try:
                    fill_value = float(fill_value)
                except ValueError:
                    pass
            result[col] = result[col].fillna(fill_value)
        else:
            print(f"Warning: Unsupported strategy '{strategy}' for column '{col}'")
    
    return result 