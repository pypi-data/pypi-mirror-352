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
    try:
        if kind == 'pairplot':
            # Get only numeric columns
            numeric_cols = df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns
            numeric_df = df[numeric_cols].copy()
            print(f"Creating pairplot with numeric columns: {numeric_cols.tolist()}")
            sns.pairplot(numeric_df)
            plt.show()
            return
        
        plt.figure(figsize=figsize)
        
        if kind == 'heatmap':
            print("\nDebug info for heatmap:")
            print("Original columns:", df.columns.tolist())
            print("Original dtypes:\n", df.dtypes)
            
            # Get only numeric columns and create a new DataFrame
            numeric_cols = df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns
            numeric_df = df[numeric_cols].copy()
            print("\nNumeric columns selected:", numeric_cols.tolist())
            
            if len(numeric_cols) < 2:
                print("Warning: Need at least 2 numeric columns for a correlation heatmap.")
                return
            
            try:
                corr = numeric_df.corr()
                print("\nCorrelation matrix shape:", corr.shape)
                sns.heatmap(corr, annot=True, cmap='coolwarm')
                plt.title('Correlation Heatmap (Numeric Columns Only)')
            except Exception as e:
                print(f"Error during correlation/heatmap: {str(e)}")
                return
            
        elif kind == 'scatter':
            if x and y:
                if pd.api.types.is_numeric_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y]):
                    sns.scatterplot(data=df, x=x, y=y)
                    sns.regplot(data=df, x=x, y=y, scatter=False)
                    plt.title(f'Scatter plot: {y} vs {x}')
                else:
                    print(f"Warning: Both {x} and {y} must be numeric for scatter plots.")
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
            plt.close()
            if x and y:
                if pd.api.types.is_numeric_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y]):
                    sns.jointplot(data=df, x=x, y=y, kind='reg')
                else:
                    print(f"Warning: Both {x} and {y} must be numeric for joint plots.")
            else:
                print("For joint plots, both x and y parameters are required.")
        else:
            print(f"Unknown plot type: {kind}")
        
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error in plot_advanced: {str(e)}")
        import traceback
        traceback.print_exc() 