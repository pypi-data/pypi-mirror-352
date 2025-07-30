Examples
========

Basic Examples
-------------

Loading and Describing Data
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from dashcamcsv import load_and_describe
    
    # Load data from a URL
    df = load_and_describe("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv")

Data Analysis
^^^^^^^^^^^^

.. code-block:: python

    from dashcamcsv import missing_report, info_summary
    
    # Check for missing values
    missing_report(df)
    
    # Get DataFrame information
    info_summary(df)

Data Cleaning
^^^^^^^^^^^^

.. code-block:: python

    from dashcamcsv import clean_data
    
    # Apply different cleaning strategies for different columns
    clean_df = clean_data(df, strategies={
        'sepal_length': 'median',  # Fill missing values with median
        'species': 'mode',         # Fill missing values with most common value
        'petal_width': 'drop',     # Drop rows where this column has missing values
        'sepal_width': 'value:5.0' # Fill missing values with a specific value
    })
    
    # Default behavior (drop rows with any NaN)
    clean_df = clean_data(df)

Visualization Examples
--------------------

Simple Plotting
^^^^^^^^^^^^^

.. code-block:: python

    from dashcamcsv import quick_plot
    
    # Create a histogram
    quick_plot(df, "sepal_length", figsize=(12, 6))
    
    # Create a bar plot for categorical data
    quick_plot(df, "species", figsize=(10, 6))

Advanced Plotting
^^^^^^^^^^^^^^

.. code-block:: python

    from dashcamcsv import plot_advanced
    
    # Create a scatter plot with regression line
    plot_advanced(df, 'sepal_length', 'sepal_width', kind='scatter', figsize=(10, 8))
    
    # Create a box plot
    plot_advanced(df, 'species', 'sepal_length', kind='box', figsize=(8, 6))
    
    # Create a correlation heatmap
    plot_advanced(df, kind='heatmap', figsize=(12, 10)) 