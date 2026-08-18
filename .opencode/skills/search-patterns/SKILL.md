---
name: search-patterns
description: "Applies Peter Morville's Search Patterns to design search and discovery experiences that actually work: the search UX/IA anatomy (query box, results, faceted navigation, suggestions), pattern libraries for search interfaces, relevance and ranking thinking, and the honest truth that search is an iterative conversation, not a single box. Use when the user says 'design search', 'search UX', 'faceted search', 'search results page', 'autocomplete', 'query understanding', 'relevance', 'search patterns', 'improve search', 'discovery experience', or when building any search interface over a data set or a knowledge base. Pairs with: vector-databases-similarity-search, qdrant-ops, n8n-rag-vector-qa, site-architecture, impeccable."
---

# Search Patterns

The premise: search is how users find things when they cannot navigate — and a
good search design is a dialogue of query, results, refinement, and iteration,
not a lone text box.

## When to use

- Designing any search interface (site search, app search, RAG chat, faceted
  product search).
- Improving relevance or the results-page layout.
- Adding autocomplete, facets, or query suggestions.

## The search anatomy

1. **Query entry** — the box plus autocomplete/suggestions that teach the system
   and guide the user.
2. **Results page** — the list, the ordering, and the summary (what matched, why).
3. **Refinement** — facets, filters, sorting, pagination for narrowing.
4. **Empty and poor results** — the moment that decides whether the user stays;
   offer alternatives, spell corrections, or broadened results instead of a dead
   end.

## Patterns that matter

- **Autocomplete / suggestions**: surface known-good queries; guides before typing
  finishes.
- **Faceted search**: orthogonal filters (category, price, date, rating) that
  combine freely; each selection re-scopes the set.
- **Result snippets**: show enough context that the user can judge relevance
  without opening the page.
- **Query understanding**: handle synonyms, stemming, typos, and intent classes;
  do not assume a literal token match.
- **Ranking**: relevance must beat raw recency or popularity for most queries; mix
  signals deliberately (see `vector-databases-similarity-search` for embeddings).

## Iteration rules

- Instrument search: track queries that return nothing, queries that users
  immediately refine, and click-through rates per result.
- Use the dead-query log as the backlog for thesaurus/alias and synonym work.
- Test ranking changes on a held-out set of real queries before shipping.
- Search is a product, not a feature: it needs owners, metrics, and a release
  cadence.

Pairs with: vector-databases-similarity-search (retrieval), qdrant-ops (vector
store ops), n8n-rag-vector-qa (RAG chat), site-architecture (navigation
complement), impeccable (results-page UI).