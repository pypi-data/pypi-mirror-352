.. dashcamcsv documentation master file, created by
   sphinx-quickstart on Wed Jun  4 13:15:06 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to dashcamcsv's documentation!
=====================================

A simple Python package with helpful utilities for data science workflows.

Features
--------

- ``load_and_describe(url: str)``: Load a CSV from a URL and print basic statistics.
- ``missing_report(df)``: Show missing value counts and percentages.
- ``info_summary(df)``: Print DataFrame shape, types, and memory usage.
- ``quick_plot(df, column, figsize=(10, 6))``: Plot a histogram or bar plot for a column with custom figure size.
- ``plot_advanced(df, x, y=None, kind='pairplot', figsize=(10, 8))``: Create advanced visualizations using seaborn with custom figure size.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   examples
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

