"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from indicium_adapters_metabarcoding import MetabarcodingAdapter


@pytest.fixture
def adapter() -> MetabarcodingAdapter:
    return MetabarcodingAdapter()


@pytest.fixture
def base_claim() -> dict:
    """A minimal 5-slot claim dict for adapter input."""
    return {
        "subject": "Taxonomy",
        "qualifier": "classified_against",
        "object": "SILVA",
        "ontology_terms": {},
        "evidence_id": "fixture-001",
    }
