---
name: python-for-data-analysis
description: Applies Wes McKinney's Python for Data Analysis to move, clean, reshape, and analyze data with pandas and NumPy: Series and DataFrame operations, indexing and selection, handling missing data, merging/joining/concatenating, grouping and aggregation, reshaping (pivot tables), and time-series analysis, plus loading data from common formats. Use when the user says 'pandas', 'DataFrame', 'groupby', 'pivot table', 'missing data', 'time series', 'merge data', 'NumPy', 'McKinney', 'data analysis in Python', or when a dataset must be cleaned, transformed, and analyzed before modeling. Pairs with: data-science-from-scratch, data-analysis, fundamentals-of-data-engineering, sheets-automation.
---
# Python for Data Analysis

Transfers McKinney's pandas discipline: data work is mostly moving, cleaning, and reshaping data — do it correctly and expressively, then model.

## When to use
- Cleaning and reshaping a dataset before analysis or modeling.
- Merging, grouping, and aggregating data across tables.
- Working with time series or messy real-world records.

## Core practice
1. Load data with the right reader and dtypes; inspect shape, dtypes, and nulls before transforming.
2. Use vectorized pandas operations over Python loops for speed and clarity.
3. Clean deliberately: handle missing data (drop, fill, interpolate) with a stated policy, dedupe, and normalize types.
4. Group and aggregate for summaries; pivot for wide formats; merge/join across keys carefully.

## Time series
- Parse datetimes, set indexes, resample and shift, rolling windows, and lag features.
- Beware timezone and frequency gotchas that silently shift data.

## Verification discipline
- Check row counts before and after every merge/group to catch silent loss.
- Assert dtypes and uniqueness after cleaning.
- Never aggregate before confirming the grouping key has no duplicates or nulls.

## Pairs with
data-science-from-scratch, data-analysis, fundamentals-of-data-engineering, sheets-automation.
