---
name: think-bayes
description: Applies Allen Downey's Think Bayes to solve real problems with Bayesian statistics in Python: the Bayesian framework (prior, likelihood, posterior), representing distributions computationally, grid-computation and conjugate approaches, estimation, hypothesis comparison with Bayes factors, and hierarchical and Gaussian methods. Use when the user says 'think bayes', 'Bayesian update', 'prior and posterior', 'Bayes factor', 'grid approximation', 'Downey bayes', 'update a belief', or when updating a belief from evidence rather than computing a single point estimate. Pairs with: think-stats, bayesian-data-analysis, machine-learning-probabilistic-perspective, formal-math-logic-verification-engine.
---
# Think Bayes

Transfers Downey's computational Bayesianism: the posterior is a distribution you compute directly, so priors and updating stay concrete.

## When to use
- Updating a belief from evidence in a structured, defensible way.
- Estimating a quantity with uncertainty when a point estimate hides too much.
- Comparing hypotheses with Bayes factors instead of null-hypothesis tests.

## Core method
1. Encode your prior as a distribution over the parameter or hypothesis.
2. Update by multiplying prior by likelihood and normalizing — the Bayesian update.
3. Summarize the posterior (mean, interval, probability of each hypothesis) for the decision.
4. Use grid approximation when the parameter space is small, conjugate methods when they fit, MCMC when it is not.

## Practice rules
- State the prior explicitly and test sensitivity to it.
- Compare hypotheses with the posterior odds and Bayes factor.
- The posterior of one step is the prior of the next — chain evidence naturally.

## Verification discipline
- Verify the update on a case with a hand-computable answer.
- Check that posterior probabilities sum to one and the likelihood is computed correctly.
- When the prior dominates, say so honestly.

## Pairs with
think-stats, bayesian-data-analysis, machine-learning-probabilistic-perspective, formal-math-logic-verification-engine.
