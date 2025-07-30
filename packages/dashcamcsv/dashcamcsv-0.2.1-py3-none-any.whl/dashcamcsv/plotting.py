import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def quick_plot(df: pd.DataFrame, column: str, figsize=(10, 6)):
    """Plot a histogram for numeric or bar plot for categorical columns.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data to plot
    column : str
        The column name to plot
    figsize : tuple, optional
        Figure size (width, height) in inches, default is (10, 6)
    """
    plt.figure(figsize=figsize)
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

def plot_advanced(df: pd.DataFrame, x: str = None, y: str = None, kind: str = 'pairplot', figsize=(10, 8)):
    """Create advanced visualizations using seaborn.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data to plot
    x : str, optional
        Column name for x-axis
    y : str, optional
        Column name for y-axis
    kind : str, optional
        Type of plot to create: 'scatter', 'box', 'violin', 'heatmap', 'pairplot', 'jointplot'
    figsize : tuple, optional
        Figure size (width, height) in inches, default is (10, 8)
    """
    plt.figure(figsize=figsize)
    
    if kind == 'pairplot':
        sns.pairplot(df)
    elif kind == 'heatmap':
        sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
    elif kind == 'scatter':
        if x and y:
            sns.scatterplot(data=df, x=x, y=y)
            sns.regplot(data=df, x=x, y=y, scatter=False)
            plt.title(f'Scatter plot: {y} vs {x}')
        else:
            print("For scatter plots, both x and y parameters are required.")
    elif kind == 'box':
        if x and y:
            sns.boxplot(data=df, x=x, y=y)
            plt.title(f'Box plot: {y} by {x}')
        else:
            print("For box plots, both x and y parameters are required.")
    elif kind == 'violin':
        if x and y:
            sns.violinplot(data=df, x=x, y=y)
            plt.title(f'Violin plot: {y} by {x}')
        else:
            print("For violin plots, both x and y parameters are required.")
    elif kind == 'jointplot':
        if x and y:
            sns.jointplot(data=df, x=x, y=y, kind='reg')
        else:
            print("For joint plots, both x and y parameters are required.")
    else:
        print(f"Unknown plot type: {kind}")
        
    plt.tight_layout()
    plt.show() 