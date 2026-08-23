"""Protocol-conformance contract for the metabarcoding adapter.

The invariants every indicium DomainAdapter must hold, plus the two this
adapter exists to satisfy for ASB: it declares ``primary_domain`` (without it a
metabarcoding paper classifies as "other"), and it resolves concepts only by
exact match (a wrong CURIE is worse than no CURIE).
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from indicium_adapters import CURRENT_API_VERSION, DomainAdapter

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def test_satisfies_the_domain_adapter_protocol(adapter):
    assert isinstance(adapter, DomainAdapter)
    # An adapter whose api_version differs is skipped by discover_adapters() with
    # only a UserWarning -- it would vanish silently rather than fail loudly.
    assert adapter.api_version == CURRENT_API_VERSION


def test_declares_primary_domain_so_asb_does_not_classify_as_other(adapter):
    assert adapter.primary_domain == "metabarcoding"
    assert adapter.domain_id == "metabarcoding"


def test_qualifiers_are_snake_case(adapter):
    """Perspicacite's asb:domainQualifier SHACL shape enforces this pattern."""
    bad = [q for q in adapter.qualifiers if not SNAKE_CASE.match(q)]
    assert not bad, f"non-snake_case qualifiers: {bad}"


def test_qualifier_count_is_in_the_expected_range(adapter):
    assert 15 <= len(adapter.qualifiers) <= 30


def test_vocabulary_terms_are_slugs(adapter):
    for term in (*adapter.subdomains, *adapter.techniques):
        assert SLUG.match(term), f"not a kebab-case slug: {term}"


def test_vocabulary_has_no_duplicates(adapter):
    assert len(set(adapter.subdomains)) == len(adapter.subdomains)
    assert len(set(adapter.techniques)) == len(adapter.techniques)


def test_subdomains_and_techniques_are_distinct(adapter):
    """The two vocabularies are read from different parts of the index (see
    ``metabarcoding.py``'s docstring) and must not collapse into one list."""
    assert set(adapter.subdomains).isdisjoint(adapter.techniques)


def test_ontology_prefixes_are_expandable_iris(adapter):
    for prefix, base in adapter.ontology_prefixes.items():
        assert SNAKE_CASE.match(prefix.lower()), prefix
        parsed = urlparse(base)
        assert parsed.scheme in ("http", "https"), f"{prefix} is not http(s)"


def test_extraction_context_names_the_domain_and_its_qualifiers(adapter):
    context = adapter.extraction_context()
    assert "metabarcoding" in context.lower()
    for qualifier in ("targets_marker", "classified_against", "denoised_by"):
        assert qualifier in context


def test_the_claim_shapes_this_domain_needs_have_a_qualifier(adapter):
    """Marker/primers, reference taxonomy, OTU/ASV method, platform, sample
    environment, diversity metric and controls -- the field notes this
    adapter was briefed against."""
    for qualifier in (
        "targets_marker",
        "amplified_with_primers",
        "classified_against",
        "denoised_by",
        "clustered_by",
        "sequenced_on",
        "sampled_from",
        "has_diversity_metric",
        "controlled_by",
    ):
        assert qualifier in adapter.qualifiers


def test_enrich_claim_is_pure(adapter):
    claim = {"subject": "Taxonomy", "predicate": "uses", "object": "SILVA"}
    before = dict(claim)
    adapter.enrich_claim(claim)
    assert claim == before, "enrich_claim mutated its input"


def test_no_accession_patterns_live_in_this_package():
    """ADR 0001: accession recognition is owned by asb-domain-core's canonical
    table. A copy here would be the duplicate-then-drift failure the ADR exists
    to prevent, so the package must not carry accession regexes."""
    import pathlib

    import indicium_adapters_metabarcoding

    pkg = pathlib.Path(indicium_adapters_metabarcoding.__file__).parent
    offenders = []
    for path in pkg.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for shape in (r"MTBLS\d", r"PXD\d", r"GSE\d", r"PRJ[EDN][AB]\d", r"SRR\d", r"UDB\d{6}"):
            if shape in text:
                offenders.append((path.name, shape))
    assert not offenders, f"accession patterns must not be duplicated here: {offenders}"
