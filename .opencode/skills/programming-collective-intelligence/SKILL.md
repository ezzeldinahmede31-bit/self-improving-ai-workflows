---
name: programming-collective-intelligence
description: Applies Toby Segaran's Programming Collective Intelligence to build recommendation and prediction systems from user data: collaborative filtering and item/item recommendation, clustering (hierarchical, k-means) for grouping users and items, searching and ranking with PageRank-like methods, and classification (naive Bayes, decision trees) applied to real-world signals. Use when the user says 'recommendation system', 'collaborative filtering', 'clustering', 'k-means', 'PageRank', 'Toby Segaran', 'collective intelligence', or when building a system that learns from many users' behavior. Pairs with: data-science-from-scratch, network-science-barabasi, social-network-analysis-wasserman, audience-psychology-analyst.
---
# Programming Collective Intelligence

Transfers Segaran's method: harness the behavior of many users into recommendations, clusters, and rankings with simple, buildable algorithms.

## When to use
- Building a recommendation engine from user preferences or behavior.
- Grouping users or items with clustering.
- Ranking items by collective signals instead of editorial rules.

## Core practice
1. Collaborative filtering: recommend items other similar users liked; item/item filtering scales better than user/user for large catalogs.
2. Clustering (hierarchical and k-means) on feature vectors to segment users or items.
3. Ranking with link/flow-based methods (PageRank-style) when relationships, not votes, carry the signal.
4. Classify with naive Bayes and decision trees on features derived from behavior.

## Practice rules
- Choose similarity metrics (cosine, Pearson, Euclidean) that match the data scale.
- Handle cold-start (new users/items) with content-based or popularity fallbacks.
- Normalize ratings (center by user mean) to remove systematic bias.

## Verification discipline
- Evaluate recommendations with held-out preferences, not the training feedback.
- Check cluster stability across runs and seeds.
- Compare collaborative vs content vs hybrid on the same held-out metric.

## Pairs with
data-science-from-scratch, network-science-barabasi, social-network-analysis-wasserman, audience-psychology-analyst.
