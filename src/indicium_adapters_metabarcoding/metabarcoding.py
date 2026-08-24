"""MetabarcodingAdapter -- the metabarcoding DomainAdapter (api_version=1)."""

from __future__ import annotations

from typing import Final

from . import _edam
from ._namespaces import METABARCODING_PREFIXES

_ENRICHABLE_SLOTS: Final[tuple[str, ...]] = ("subject", "object", "qualifier")

# SSSOM justification for a label / exact-synonym string match. Every CURIE this
# adapter emits comes from exact-after-normalisation matching against the
# vendored EDAM index, so this is the only justification it can honestly claim.
_LEXICAL: Final[str] = "semapv:LexicalMatching"


class MetabarcodingAdapter:
    """Amplicon sequencing of a marker gene to census the taxa present in a sample.

    Owns the tier-3 concerns only (ADR 0001): the classification vocabulary and
    claim/ontology enrichment. It deliberately does **not** recognise repository
    accessions (ENA, SRA, GEO, BioProject) or reference-database accessions
    (SILVA, UNITE, BOLD) in article text -- those belong to the canonical
    accession table in ``asb-domain-core``, and a second copy of those patterns
    here would be the duplicate-then-drift failure ADR 0001 exists to prevent.
    What this adapter contributes for identifiers is ``ontology_prefixes``, so a
    consumer can expand the CURIEs that tier produces.

    The concept vocabulary is read from EDAM, cut from four roots: Metabarcoding
    itself, plus Taxonomy, Phylogenetics and Microbial ecology. EDAM does not
    file the latter three underneath Metabarcoding -- Metabarcoding is in fact
    the sole child of Microbial ecology, and Taxonomy and Phylogenetics are
    unconnected leaves -- yet a metabarcoding paper claims all three: an amplicon
    study assigns taxonomy, builds a phylogenetic tree and reports community
    composition. See ``data/build_edam_index.py`` for the full rationale.

    Metabarcoding is itself a leaf topic in EDAM, so there is no subtree under
    the domain root to read a decomposition off. Reading around that gap put the
    two lists the wrong way up: ``subdomains`` came from the additional roots'
    labels, which are neighbouring SCIENCES (microbial ecology, phylogenetics,
    taxonomy) rather than parts of this one, while the named variants of the
    practice -- DNA, RNA, environmental, eDNA, eRNA metabarcoding -- sat under
    ``techniques``, where they name no assay.

    The 2026-08-25 cross-domain audit corrected the inversion: the variants are
    the subdomains, and the techniques are the two amplicon assays this field
    can claim alone. The 16S, ITS and 18S markers are deliberately absent --
    metagenomics declared them too, and a term two sciences both utter cannot
    say which of them a paper belongs to, so it is withheld from both. The
    generated EDAM index is still shipped and still answers ``enrich_claim``.

    Every qualifier matches ``^[a-z][a-z0-9_]*$`` (snake_case), required because
    Perspicacite routes adapter qualifiers onto the open ``asb:domainQualifier``
    slot whose SHACL shape enforces that pattern. Enforced by
    ``tests/test_protocol_conformance.py``.
    """

    domain_id = "metabarcoding"
    api_version = 1

    # ASB's classification layer reads `primary_domain` in preference to
    # `domain_id`; without it a metabarcoding paper classifies as "other".
    primary_domain = "metabarcoding"

    qualifiers: frozenset[str] = frozenset(
        {
            # --- Marker, primers and amplification -----------------------------
            "targets_marker",  # object is the marker gene/region (16S, 18S, ITS, COI)
            "amplified_with_primers",  # object is the primer pair used (515F/806R)
            "spans_hypervariable_region",  # object is the amplified region (V3-V4, ITS1)
            # --- Sequencing ------------------------------------------------------
            "sequenced_on",  # object is the sequencing platform (MiSeq, Sequel II)
            "demultiplexed_by",  # object is the barcode/index demultiplexing tool
            # --- Bioinformatic processing -----------------------------------------
            "quality_filtered_by",  # object is the read quality-filtering/trimming tool
            "denoised_by",  # object is the ASV denoising algorithm (DADA2, Deblur)
            "clustered_by",  # object is the OTU-clustering algorithm or tool
            "clustered_at",  # object is the sequence-identity threshold used
            "chimera_checked_by",  # object is the chimera-detection tool
            "represented_by_sequence",  # object is the representative ASV/OTU sequence id
            # --- Taxonomic classification -----------------------------------------
            "classified_against",  # object is the reference taxonomy database (SILVA, UNITE, BOLD)
            "classified_by",  # object is the taxonomic classifier or algorithm
            "assigned_to_taxon",  # object is the taxon name or rank assigned
            # --- Sample and ecological context --------------------------------------
            "sampled_from",  # object is the environment or habitat the sample came from
            "collected_with",  # object is the sampling device or protocol
            "hosts",  # object is the host organism the sample was taken from
            "co_occurs_with",  # object is another taxon detected in the same community
            # --- Community and diversity metrics -----------------------------------
            "has_diversity_metric",  # object is the alpha- or beta-diversity measure reported
            "rarefied_to",  # object is the rarefaction depth used
            "differs_in_abundance_by",  # object is the differential-abundance statistic/method
            "correlates_with",  # object is an environmental variable or metadata field
            # --- Quality control and validation --------------------------------------
            "controlled_by",  # object is the control used (negative, mock community, blank)
            "validated_by",  # object is an orthogonal identification method (morphology, qPCR)
            "deposited_in",  # object is the archive the reads were deposited in
        }
    )

    ontology_prefixes: dict[str, str] = dict(METABARCODING_PREFIXES)

    # ---- vocabulary this field alone can claim -----------------------------
    # Not read from the index; see the class docstring for the inversion it had.

    subdomains: tuple[str, ...] = (
        "dna-metabarcoding",
        "rna-metabarcoding",
        "edna-metabarcoding",
        "erna-metabarcoding",
        "environmental-metabarcoding",
        "diet-metabarcoding",
    )

    techniques: tuple[str, ...] = (
        "coi-amplicon-sequencing",
        "12s-rrna-amplicon-sequencing",
    )

    # ---- protocol methods --------------------------------------------------

    def extraction_context(self) -> str:
        """Return the domain instructions handed to the extraction model."""
        return (
            "Domain: metabarcoding -- amplicon sequencing of a marker gene (16S, "
            "18S, ITS, COI) to census the taxa present in a sample. Name subjects "
            "and objects with EDAM terminology where one applies (for example "
            "'taxonomic classification', 'phylogenetic tree construction'), using "
            "the singular preferred label rather than a paraphrase. Prefer a "
            "concrete marker, primer pair, tool or database name over a generic "
            "word: '515F/806R' rather than 'the primers', 'DADA2' rather than "
            "'the denoising tool', 'SILVA' rather than 'the reference database'. "
            "Keep a raw read, an ASV/OTU and the taxon it was assigned distinct. "
            "Domain qualifiers available in addition to the base set: "
            + ", ".join(sorted(self.qualifiers))
            + "."
        )

    def enrich_claim(self, claim: dict) -> dict:
        """Attach EDAM CURIEs to the slots whose text names an EDAM concept.

        Pure: returns a new dict and never mutates the input or its nested maps.

        Matching is exact after case-folding and whitespace collapse. Substring
        and fuzzy matching over an ontology manufacture confident-looking wrong
        CURIEs ("Taxonomy" inside "Molecular taxonomy"), and a wrong identifier
        is worse than no identifier.

        A slot that carries text but resolves to nothing is recorded under
        ``ontology_terms_unmatched`` rather than passed over. Silence would make
        "this text is not an EDAM concept" indistinguishable from "no attempt
        was made", which is the distinction a downstream mapping set needs.
        """
        out = dict(claim)
        terms: dict[str, str] = dict(out.get("ontology_terms") or {})
        justifications: dict[str, str] = dict(out.get("ontology_term_justifications") or {})
        unmatched: dict[str, str] = dict(out.get("ontology_terms_unmatched") or {})

        for slot in _ENRICHABLE_SLOTS:
            if slot in terms:
                continue  # another adapter already resolved this slot
            value = out.get(slot)
            if not isinstance(value, str) or not value.strip():
                continue
            curie = _edam.lookup(value)
            if curie:
                terms[slot] = curie
                justifications[slot] = _LEXICAL
                unmatched.pop(slot, None)
            else:
                unmatched[slot] = value

        if terms:
            out["ontology_terms"] = terms
            out["ontology_term_justifications"] = justifications
        if unmatched:
            out["ontology_terms_unmatched"] = unmatched
        elif "ontology_terms_unmatched" in out:
            # A slot that was unmatched on a previous pass and now resolves
            # must not leave a stale, now-wrong "unmatched" record behind --
            # see the class docstring on why this dict has to stay accurate.
            del out["ontology_terms_unmatched"]
        return out
