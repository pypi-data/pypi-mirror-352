import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def quick_plot(df: pd.DataFrame, column: str):
    """Plot a histogram for numeric or bar plot for categorical columns."""
    if pd.api.types.is_numeric_dtype(df[column]):
        df[column].hist(bins=30)
        plt.xlabel(column)
        plt.ylabel('Frequency')
        plt.title(f'Histogram of {column}')
    else:
        df[column].value_counts().plot(kind='bar')
        plt.xlabel(column)
        plt.ylabel('Count')
        plt.title(f'Bar plot of {column}')
    plt.show() 

def plot_advanced(df: pd.DataFrame, x: str, y: str = None, kind: str = 'pairplot'):
    """Create advanced visualizations using seaborn.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data
    x : str
        Column name for x-axis
    y : str, optional
        Column name for y-axis (not needed for some plot types)
    kind : str, optional
        Type of plot to create. Options include:
        - 'pairplot': Creates a pairplot of numeric columns (ignores x and y)
        - 'scatter': Creates a scatter plot with regression line
        - 'box': Creates a boxplot
        - 'violin': Creates a violin plot
        - 'heatmap': Creates a correlation heatmap (ignores x and y)
    """
    plt.figure(figsize=(10, 6))
    
    if kind == 'pairplot':
        sns.pairplot(df)
    elif kind == 'scatter':
        if y is None:
            raise ValueError("y parameter is required for scatter plots")
        sns.regplot(x=x, y=y, data=df)
        plt.title(f'Scatter plot with regression line: {x} vs {y}')
    elif kind == 'box':
        if y is None:
            sns.boxplot(x=x, data=df)
            plt.title(f'Box plot of {x}')
        else:
            sns.boxplot(x=x, y=y, data=df)
            plt.title(f'Box plot of {y} grouped by {x}')
    elif kind == 'violin':
        if y is None:
            sns.violinplot(x=x, data=df)
            plt.title(f'Violin plot of {x}')
        else:
            sns.violinplot(x=x, y=y, data=df)
            plt.title(f'Violin plot of {y} grouped by {x}')
    elif kind == 'heatmap':
        corr = df.select_dtypes(include=['number']).corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)
        plt.title('Correlation Heatmap')
    else:
        raise ValueError(f"Unknown plot type: {kind}")
    
    plt.tight_layout()
    plt.show() 