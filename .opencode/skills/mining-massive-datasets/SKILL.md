---
name: mining-massive-datasets
description: Applies Leskovec, Rajaraman & Ullman's Mining of Massive Datasets to process data too big for main memory: map-reduce and distributed algorithms, locality-sensitive hashing, frequent itemsets, clustering at scale, page-rank and link analysis, and recommendation systems. Use when the user says 'mining massive datasets', 'locality sensitive hashing', 'frequent itemsets', 'page rank', 'map reduce algorithms', 'scalable clustering', 'Rajaraman Ullman', or when a data-mining algorithm must scale to huge data. Pairs with: data-mining-practical-ml, fundamentals-of-data-engineering, data-intensive-application-design, distributed-systems-concepts-design.
---
# Mining of Massive Datasets

## When to use
Use when a data-mining algorithm must scale to huge data, or when the user asks about locality-sensitive hashing, frequent itemsets, or page rank.

## Core mechanics
- Distribute computation with map-reduce style algorithms.
- Use locality-sensitive hashing for similarity at scale.
- Mine frequent itemsets with the classic algorithms.
- Cluster data that does not fit in memory.
- Run link analysis such as page rank.
- Build recommendation systems from scalable primitives.

## Verification
- Verify approximate results against exact results on a small dataset.
- Check that the algorithm's memory bound holds.
- Test on synthetic data with known structure.
