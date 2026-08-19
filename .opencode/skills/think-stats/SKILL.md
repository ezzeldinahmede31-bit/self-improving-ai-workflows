---
name: think-stats
description: Applies Allen Downey's Think Stats to reason about real data with statistics and Python: distributions (PMF, CDF), exploratory data analysis, hypothesis testing and significance, correlation, regression, and estimation with resampling. A probability and statistics course built around real datasets and code. Use when the user says 'think stats', 'probability distribution', 'CDF', 'hypothesis test', 'p-value', 'correlation', 'linear regression', 'resampling', 'Downey', or when analyzing data and needs the statistical reasoning made concrete and visual. Pairs with: think-bayes, data-science-from-scratch, data-analysis, bayesian-data-analysis.
---
# Think Stats

Transfers Downey's code-first statistics: every statistical idea is made concrete by computing it directly on data, then reasoned about.

## When to use
- Exploring a dataset with distributions and summary statistics.
- Testing a hypothesis or estimating a parameter honestly.
- Teaching yourself statistics by computing everything from data.

## Core practice
1. Look at distributions first: PMFs and CDFs reveal shape, outliers, and errors before any test.
2. Compute summary statistics that match the distribution (median for skewed data, mean for symmetric).
3. Test hypotheses with resampling (permutation, bootstrap) to build intuition for what significance means.
4. Fit and check regression; verify residuals and correlation assumptions.

## Rules
- Correlation is not causation: state the confounders you cannot rule out.
- A p-value is evidence under a null model, not the probability the hypothesis is true.
- Report effect size and confidence intervals alongside significance.

## Verification discipline
- Validate every computed statistic against a hand-checked small example.
- Re-run tests with a different seed to confirm stability.
- When results surprise you, go back to the distribution plot before trusting the number.

## Pairs with
think-bayes, data-science-from-scratch, data-analysis, bayesian-data-analysis.
