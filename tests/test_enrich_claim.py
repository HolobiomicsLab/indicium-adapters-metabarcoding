"""Behavioural contract for MetabarcodingAdapter.enrich_claim."""

from __future__ import annotations

from indicium_adapters_metabarcoding import MetabarcodingAdapter


def test_known_label_resolves_to_an_edam_curie(adapter: MetabarcodingAdapter):
    out = adapter.enrich_claim({"subject": "Taxonomy", "object": "Phylogenetics"})
    assert out["ontology_terms"]["subject"] == "edam:topic_0637"
    assert out["ontology_terms"]["object"] == "edam:topic_3293"
    assert out["ontology_term_justifications"]["subject"] == "semapv:LexicalMatching"


def test_a_synonym_resolves_to_the_same_curie_as_its_preferred_label(adapter):
    preferred = adapter.enrich_claim({"subject": "Microbial ecology"})
    synonym = adapter.enrich_claim({"subject": "Microbiome"})
    assert preferred["ontology_terms"]["subject"] == synonym["ontology_terms"]["subject"]


def test_lookup_is_case_and_whitespace_insensitive(adapter):
    spaced = adapter.enrich_claim({"subject": "  tAxOnOmY  "})
    exact = adapter.enrich_claim({"subject": "Taxonomy"})
    assert spaced["ontology_terms"]["subject"] == exact["ontology_terms"]["subject"]


def test_unresolved_text_is_recorded_not_silently_dropped(adapter):
    out = adapter.enrich_claim({"subject": "a phrase that is not an EDAM concept"})
    assert out["ontology_terms_unmatched"]["subject"] == "a phrase that is not an EDAM concept"
    assert "ontology_terms" not in out


def test_substring_of_a_concept_does_not_resolve(adapter):
    """A prefix of a real index entry must not pick that entry up -- a wrong
    CURIE is worse than no CURIE."""
    for prefix in ("metabarcod", "microbial"):
        assert adapter.enrich_claim({"subject": prefix}).get("ontology_terms") is None


def test_an_already_resolved_slot_is_left_to_its_owner(adapter):
    claim = {"subject": "Taxonomy", "ontology_terms": {"subject": "NCBITaxon:2"}}
    out = adapter.enrich_claim(claim)
    assert out["ontology_terms"]["subject"] == "NCBITaxon:2"


def test_empty_and_non_string_slots_are_skipped(adapter):
    out = adapter.enrich_claim({"subject": "", "object": None, "qualifier": 42})
    assert "ontology_terms" not in out
    assert "ontology_terms_unmatched" not in out


def test_a_declared_qualifier_can_still_resolve_if_it_happens_to_be_an_edam_label(adapter):
    """Unlike the genomics adapter, this one has no own-vocabulary skip: none of
    its qualifiers collide with an EDAM label in the shipped index, so every
    qualifier value is simply looked up like any other slot text."""
    out = adapter.enrich_claim({"qualifier": "classified_against"})
    assert out.get("ontology_terms") is None
    assert out["ontology_terms_unmatched"]["qualifier"] == "classified_against"


def test_enrich_claim_does_not_mutate_nested_maps(adapter):
    original_terms = {"object": "edam:topic_0637"}
    claim = {"subject": "Taxonomy", "ontology_terms": original_terms}
    out = adapter.enrich_claim(claim)
    assert out["ontology_terms"] is not original_terms
    assert original_terms == {"object": "edam:topic_0637"}


def test_a_slot_that_now_resolves_drops_its_stale_unmatched_record(adapter):
    """A claim can already carry an ``ontology_terms_unmatched`` entry for a
    slot from an earlier pass (e.g. before its text was corrected). If this
    pass resolves that same slot, the stale unmatched record must not survive
    -- otherwise a slot with a fresh CURIE would still read as unresolved."""
    claim = {
        "subject": "Taxonomy",
        "ontology_terms_unmatched": {"subject": "stale text from an earlier pass"},
    }
    out = adapter.enrich_claim(claim)
    assert out["ontology_terms"]["subject"] == "edam:topic_0637"
    assert "ontology_terms_unmatched" not in out
