---
name: literature-search
description: Search academic literature using Semantic Scholar, arXiv, and OpenAlex APIs. Returns structured JSONL with title, authors, year, venue, abstract, citations, and BibTeX. Use when the user needs to find papers, check related work, or build a bibliography.
argument-hint: [search-query]
---

# Literature Search

Search multiple academic databases to find relevant papers.

## Input

- `$ARGUMENTS` — The search query (natural language)

## Scripts (installed in this skill — use these paths)

> Semantic Scholar direct search, arXiv direct search, merge/dedupe and
> BibTeX helpers used to live in the companion `deep-research` skill, which
> is not installed here — those commands were removed on 2026-10-12 rather
> than point at missing files. Never harvest API keys from another person's
> files; use your own env vault.

### OpenAlex (broadest coverage, free, no API key)
```bash
python ~/.claude/skills/literature-search/scripts/search_openalex.py \
  --query "QUERY" --max-results 20 --year-range 2022-2026 \
  --min-citations 5 -o results_openalex.jsonl
```

### Merge & Deduplicate (manual — no merge script ships with this skill)
Merge the per-source JSONL files, dedupe by DOI/title, and write `merged.jsonl`.

### CrossRef (DOI-based lookup, broadest type coverage)
```bash
python ~/.claude/skills/literature-search/scripts/search_crossref.py \
  --query "QUERY" --rows 10 --output results_crossref.jsonl
```

Key flags: `--bibtex` (output .bib format), `--rows N`

### Download arXiv Source (get .tex files)
```bash
python ~/.claude/skills/literature-search/scripts/download_arxiv_source.py \
  --title "Paper Title" --output-dir arxiv_papers/
```

Key flags: `--arxiv-id 1706.03762`, `--metadata`, `--max-results N`

### Generate BibTeX from results (manual — no BibTeX script ships with this skill)
Convert `merged.jsonl` to `references.bib` (one @article per record).

## Workflow

1. Expand the user's query into 2-4 complementary search queries
2. Run Semantic Scholar search (primary) with expanded queries
3. Run arXiv for very recent preprints (< 3 months)
4. Optionally run OpenAlex for broader coverage
5. Merge and deduplicate results
6. Rank by: citations (0.3) + recency (0.3) + venue quality (0.2) + relevance (0.2)
7. Present structured results table

## Venue Quality Tiers

**Tier 1:** NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, CVPR, ICCV, ECCV, KDD, AAAI, IJCAI, SIGIR, WWW
**Tier 2:** AISTATS, UAI, COLT, COLING, EACL, WACV, JMLR, TACL
**Tier 3:** Workshops, arXiv preprints — mark with `(preprint)`

## Output Format

Present results as a table + detailed entries with BibTeX keys. Always note preprint status.

## Related Skills
- Downstream: [citation-management](../citation-management/), [literature-review](../literature-review/), [related-work-writing](../related-work-writing/)
- See also: [deep-research](../deep-research/), [novelty-assessment](../novelty-assessment/)
