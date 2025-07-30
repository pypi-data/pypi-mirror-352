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