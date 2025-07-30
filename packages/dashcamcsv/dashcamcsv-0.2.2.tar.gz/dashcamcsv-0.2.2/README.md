# dashcamcsv

A simple Python package with helpful utilities for data science workflows.

## Features
- `load_and_describe(url: str)`: Load a CSV from a URL and print basic statistics.
- `missing_report(df)`: Show missing value counts and percentages.
- `info_summary(df)`: Print DataFrame shape, types, and memory usage.
- `quick_plot(df, column, figsize=(10, 6))`: Plot a histogram or bar plot for a column with custom figure size.
- `plot_advanced(df, x, y=None, kind='pairplot', figsize=(10, 8))`: Create advanced visualizations using seaborn with custom figure size.

## Installation
```bash
pip install dashcamcsv
```

## Usage
```python
from dashcamcsv import load_and_describe, missing_report, info_summary, quick_plot, plot_advanced

# Basic example
df = load_and_describe("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv")
missing_report(df)
info_summary(df)
quick_plot(df, "sepal_length", figsize=(12, 6))  # Customize figure size

# Advanced visualizations with seaborn
plot_advanced(df, 'sepal_length', 'sepal_width', kind='scatter', figsize=(10, 8))  # Scatter plot with regression line
plot_advanced(df, 'species', 'sepal_length', kind='box', figsize=(8, 6))  # Box plot
plot_advanced(df, kind='heatmap', figsize=(12, 10))  # Correlation heatmap
```

## Changelog
- v0.2.2: Fixed plotting functions to handle categorical data better
- v0.2.1: Added compatibility with Python 3.8+
- v0.2.0: Added figsize parameter to plotting functions
- v0.1.0: Initial release
