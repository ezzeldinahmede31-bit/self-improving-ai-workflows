---
name: geewax-pagination-filtering-masks
description: "Applies the pagination, filtering, and field-mask chapters of JJ Geewax's API Design Patterns to make list/read APIs scalable, queryable, and bandwidth-friendly: cursor-based and page-token pagination instead of naive offsets, filtering with a structured syntax, and field masks so a client requests only the fields it needs and can do partial updates safely. Use when the user says 'pagination design', 'page token', 'cursor pagination', 'filter my list API', 'field mask', 'partial update', 'PATCH semantics', 'only return these fields', 'API list endpoint', 'Geewax pagination', or when a list endpoint must stay fast as the data grows. Pairs with: api-design-patterns, api-long-running-operations, api-versioning-compatibility, building-data-heavy-applications, restful-web-apis."
---

# Pagination, Filtering, and Field Masks

The standard list method in Geewax's resource-oriented API design stays fast
and friendly as data grows through three disciplined features: pagination,
filtering, and field masks.

## When to use

- Designing a list/list-fields endpoint that must handle large result sets.
- A client should not pay for fields it never reads.
- A client needs to update one field without resending the whole resource.

## Pagination

- **Cursor / page-token pagination** — the API returns an opaque token that
  encodes the position in the result set; the client passes it back as `pageToken`
  to get the next page. The token encodes where you are, not the number of rows to
  skip.
- Cursor pagination stays correct when rows are inserted or removed mid-scan,
  unlike offset pagination, and it keeps queries index-friendly.
- The response carries `nextPageToken` (empty when no further pages) and the
  requested `pageSize` capped at a server maximum.
- Never expose raw offsets in a resource-oriented API; offset pagination
  degrades with a shifting dataset.

## Filtering

- Filtering narrows the result set server-side so pagination stays meaningful.
- A structured filter expression (`state=ACTIVE AND price>10`) beats ad-hoc
  query parameters for composability.
- Keep the filter grammar small, documented, and safe: only whitelisted fields,
  only comparison operators the storage layer can push down.
- Apply filtering before pagination — the page size bounds the filtered set,
  not the raw set.

## Field masks

- A **field mask** is a list of paths (`name,address.city`) describing which
  fields the client wants.
- Read: the response returns only the masked fields, saving bandwidth.
- Update: a partial update applies only the masked paths, so a client can
  change one field without a full read-modify-write cycle.
- Validate mask paths against the schema; reject unknown paths instead of
  silently ignoring them.

Pairs with: api-design-patterns (the standard methods these features belong
to), api-long-running-operations, api-versioning-compatibility (masks make
additive growth safe), building-data-heavy-applications (large result sets),
restful-web-apis.
