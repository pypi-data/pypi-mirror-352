Usage
=====

Basic Usage
----------

Here's how to use the basic functionality of dashcamcsv:

.. code-block:: python

    from dashcamcsv import load_and_describe, missing_report, info_summary

    # Load a dataset from a URL
    df = load_and_describe("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv")
    
    # Generate a report of missing values
    missing_report(df)
    
    # Get summary information about the DataFrame
    info_summary(df)

Data Cleaning
------------

The package provides flexible data cleaning capabilities:

.. code-block:: python

    from dashcamcsv import clean_data
    
    # Clean data with different strategies per column
    clean_df = clean_data(df, strategies={
        'sepal_length': 'median',  # Fill missing values with median
        'species': 'mode',         # Fill missing values with most common value
        'petal_width': 'drop',     # Drop rows where this column has missing values
        'sepal_width': 'value:5.0' # Fill missing values with a specific value
    })
    
    # Available strategies:
    # - 'drop': Drop rows where this column has NaN
    # - 'mean': Fill NaN with column mean (numeric columns only)
    # - 'median': Fill NaN with column median (numeric columns only)
    # - 'mode': Fill NaN with most frequent value
    # - 'zero': Fill NaN with zero (numeric columns only)
    # - 'value:X': Fill NaN with specific value X

Visualization
------------

The package provides simple visualization functions:

.. code-block:: python

    from dashcamcsv import quick_plot, plot_advanced
    
    # Create a simple histogram
    quick_plot(df, "sepal_length", figsize=(12, 6))
    
    # Create more advanced visualizations
    plot_advanced(df, 'sepal_length', 'sepal_width', kind='scatter', figsize=(10, 8))
    plot_advanced(df, 'species', 'sepal_length', kind='box', figsize=(8, 6))
    plot_advanced(df, kind='heatmap', figsize=(12, 10)) 