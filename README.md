# indicium-adapters-metabarcoding

A `metabarcoding` `DomainAdapter` for the
[indicium](https://github.com/HolobiomicsLab/indicium) ecosystem: classification
vocabulary and claim/ontology enrichment for amplicon sequencing of a marker
gene (16S, 18S, ITS, COI) to census the taxa present in a sample.

```python
from indicium_adapters_metabarcoding import MetabarcodingAdapter

adapter = MetabarcodingAdapter()
adapter.enrich_claim({"subject": "Taxonomy", "qualifier": "classified_against", "object": "SILVA"})
# {'subject': 'Taxonomy', 'qualifier': 'classified_against', 'object': 'SILVA',
#  'ontology_terms': {'subject': 'edam:topic_0637'},
#  'ontology_term_justifications': {'subject': 'semapv:LexicalMatching'},
#  'ontology_terms_unmatched': {'object': 'SILVA'}}
```

It owns **tier-3 concerns only** (ADR 0001): the classification vocabulary and
claim/ontology enrichment. It does **not** scan article text for repository or
reference-database accessions (ENA, SRA, SILVA, UNITE, BOLD) — that recognition
belongs to the canonical accession table in `asb-domain-core`, and a second copy
of those patterns here would be the duplicate-then-drift failure ADR 0001 exists
to prevent. What this package contributes for identifiers is the
`ontology_prefixes` table that *expands* a CURIE some other component already
recognised.

## Where the vocabulary came from

The concept index is cut from EDAM through EBI OLS4, from four recorded roots:

| Root | EDAM topic | Why it is named |
|---|---|---|
| Metabarcoding | `topic_4038` | the domain itself |
| Taxonomy | `topic_0637` | an amplicon study assigns taxonomy to every read |
| Phylogenetics | `topic_3293` | and often builds a tree from the same reads |
| Microbial ecology | `topic_3697` | and reports the resulting community composition |

EDAM does not file the latter three underneath Metabarcoding. The relationship
in fact runs the other way for one of them — **Metabarcoding is EDAM's sole
child of Microbial ecology** — and Taxonomy and Phylogenetics are themselves
leaf topics with no children of their own. Walking from any of the four roots
therefore reaches nothing beyond their own four labels and synonyms: **13 index
entries** in total. That is a small vocabulary, and it is the honest one —
padding it with hand-picked labels EDAM does not carry would manufacture wrong
CURIEs, which is worse than no CURIE. The full rationale, and how a future EDAM
release would change this, is recorded in
`data/build_edam_index.py`.

### `subdomains` and `techniques` split an unusually shallow tree

Metabarcoding is a leaf topic, so — unlike the sibling genomics and astronomy
adapters — there is no subtree under the domain root to read `subdomains` and
`techniques` from separately. Both are still read from the generated index,
just from two different parts of it:

- **`subdomains`** (3: `microbial-ecology`, `phylogenetics`, `taxonomy`) — the
  labels of the three additional roots, i.e. the fields the index actually
  reached beyond Metabarcoding itself.
- **`techniques`** (5: `dna-metabarcoding`, `edna-metabarcoding`,
  `environmental-metabarcoding`, `erna-metabarcoding`, `rna-metabarcoding`) —
  the domain root's own EDAM-recorded exact synonyms, which happen to name the
  practice's molecule-level variants.

Neither list is hand-listed; both are read off the same walk that builds the
concept index, so a future EDAM release that adds children under any of the
four roots grows both without an editor deciding anything.

## Enrichment is exact-match

`enrich_claim` walks the `subject`, `object` and `qualifier` slots and resolves
each against the EDAM index with case-folding and whitespace collapse only — no
substring, no fuzzy matching. Substring matching over an ontology manufactures
confident-looking wrong CURIEs ("Taxonomy" inside "Molecular taxonomy"), and a
wrong identifier is worse than no identifier. A slot that carries text but
resolves to nothing is recorded under `ontology_terms_unmatched` rather than
passed over, so "this text is not an EDAM concept" stays distinguishable from
"no attempt was made".

## What it does not do

- No repository- or database-accession regexes (ENA, SRA, SILVA, UNITE, BOLD) —
  recognition of those lives in `asb-domain-core`.
- No amplicon-processing pipeline, no read filtering, no taxonomy assignment.
  This package classifies and annotates already-extracted claims; it never
  reads sequence data or article text itself.
- No fuzzy or substring matching against EDAM.

## Qualifiers

25, all snake_case, grouped by what a metabarcoding claim needs to describe:
marker and primers (`targets_marker`, `amplified_with_primers`,
`spans_hypervariable_region`), sequencing (`sequenced_on`, `demultiplexed_by`),
bioinformatic processing (`denoised_by`, `clustered_by`, `clustered_at`,
`chimera_checked_by`, …), taxonomic classification (`classified_against`,
`classified_by`, `assigned_to_taxon`), sample and ecological context
(`sampled_from`, `collected_with`, `hosts`, `co_occurs_with`), community and
diversity metrics (`has_diversity_metric`, `rarefied_to`,
`differs_in_abundance_by`, `correlates_with`), and quality control
(`controlled_by`, `validated_by`, `deposited_in`).

Every qualifier matches `^[a-z][a-z0-9_]*$` because Perspicacité routes adapter
qualifiers onto the open `asb:domainQualifier` slot, whose SHACL shape enforces
that pattern.

## `ontology_prefixes`

| Prefix | Role |
|---|---|
| `NCBITaxon`, `ENVO`, `OBI` | OBO ontologies (organism, environment, protocol) |
| `edam` | this package's own concept spine (lower-case: the prefix `_edam.py` mints) |
| `SILVA`, `UNITE`, `BOLD` | the reference databases taxonomy is typically assigned against |
| `ENA` | the INSDC archive amplicon reads are typically deposited in |
| `MIxS` | the GSC checklist metadata terms are typically drawn from |

None of these are mined from text by this package — see "What it does not do"
above.

## Install

```bash
uv pip install -e .
```

The `indicium.adapters` entry point makes it discoverable via
`indicium_adapters.discover_adapters()` on install — no configuration.

## Regenerating the bundled index

```bash
python -m indicium_adapters_metabarcoding.data.build_edam_index
```

Reads EDAM through EBI OLS4, records the roots it was cut from, and emits the
`subdomains` and `techniques` slug lists off the same walk. Regenerate on an
EDAM release. Never runs at install or import time.

## Licence

MIT.
