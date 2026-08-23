# Changelog

## 0.1.0

First release.

- `MetabarcodingAdapter`, api_version 1, `domain_id` and `primary_domain`
  `metabarcoding`.
- Concept index built from EDAM, cut from four roots: Metabarcoding
  (`topic_4038`), Taxonomy (`topic_0637`), Phylogenetics (`topic_3293`) and
  Microbial ecology (`topic_3697`). All four are near-leaf topics in current
  EDAM — Metabarcoding has no children of its own and is itself the sole child
  of Microbial ecology — so the index holds 13 label/synonym entries.
- `subdomains` (3: `microbial-ecology`, `phylogenetics`, `taxonomy`) read from
  the additional roots' own labels; `techniques` (5: variants of the domain
  root's own EDAM synonyms — DNA, eDNA, environmental, eRNA and RNA
  metabarcoding) read from the same generated index. Both properties are
  generated, not hand-listed.
- 25 domain qualifiers covering marker/primers, sequencing platform,
  bioinformatic processing (denoising, OTU/ASV clustering, chimera checking),
  taxonomic classification, sample and ecological context, community/diversity
  metrics, and quality control.
- `ontology_prefixes` for NCBITaxon, ENVO, OBI, EDAM, SILVA, UNITE, BOLD, ENA
  and MIxS — expansion only; recognition of accessions in text stays in
  `asb-domain-core` per ADR 0001.
- `enrich_claim` resolves `subject` / `object` / `qualifier` against the EDAM
  index by exact match after normalisation, and records any unresolved slot
  text under `ontology_terms_unmatched`.
