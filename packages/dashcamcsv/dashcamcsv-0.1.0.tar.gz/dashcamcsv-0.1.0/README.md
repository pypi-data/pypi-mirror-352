# dashcamcsv

A simple Python package with helpful utilities for data science workflows.

## Features
- `load_and_describe(url: str)`: Load a CSV from a URL and print basic statistics.
- `missing_report(df)`: Show missing value counts and percentages.
- `info_summary(df)`: Print DataFrame shape, types, and memory usage.
- `quick_plot(df, column)`: Plot a histogram or bar plot for a column.
- `plot_advanced(df, x, y=None, kind='pairplot')`: Create advanced visualizations using seaborn.

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
quick_plot(df, "sepal_length")

# Advanced visualizations with seaborn
plot_advanced(df, 'sepal_length', 'sepal_width', kind='scatter')  # Scatter plot with regression line
plot_advanced(df, 'species', 'sepal_length', kind='box')  # Box plot
plot_advanced(df, kind='heatmap')  # Correlation heatmap
```
