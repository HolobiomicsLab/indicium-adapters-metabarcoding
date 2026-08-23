"""Integrity contract for the shipped EDAM concept index.

The index cannot be checked against EDAM offline, so what is pinned here is
everything that can go wrong without a network call: a CURIE that is not an
EDAM accession, a key the lookup normaliser could never produce, and a
subdomain or technique slug in the classification vocabulary that no longer
names a concept -- or, for techniques, a synonym -- the index can resolve.
"""

from __future__ import annotations

import re

from indicium_adapters_metabarcoding import _edam
from indicium_adapters_metabarcoding.data.build_edam_index import DOMAIN_ROOT

EDAM_CURIE = re.compile(r"^edam:topic_\d{4}$")

INDEX = _edam._payload()["index"]


def test_every_curie_is_an_edam_accession():
    bad = sorted(curie for curie in INDEX.values() if not EDAM_CURIE.match(curie))
    assert not bad, f"not EDAM accessions: {bad}"


def test_every_key_is_already_normalised():
    """A key the normaliser cannot produce is a lookup that can never fire."""
    unreachable = sorted(key for key in INDEX if _edam._normalise(key) != key)
    assert not unreachable, f"unreachable keys: {unreachable}"


def test_the_recorded_roots_are_edam_iris():
    assert _edam.roots()
    for iri in _edam.roots():
        assert iri.startswith(_edam.EDAM_PREFIX), iri


def test_the_domain_root_is_one_of_the_recorded_roots():
    assert DOMAIN_ROOT in _edam.roots()


def test_every_subtopic_resolves_through_the_index():
    """Binds the classification vocabulary to the concept index, so a subdomain
    cannot survive an EDAM release that renamed or dropped its topic."""
    unresolved = [
        slug for slug in _edam.subtopics() if _edam.lookup(slug.replace("-", " ")) is None
    ]
    assert not unresolved, f"subdomains with no EDAM concept: {unresolved}"


def test_every_technique_resolves_through_the_index():
    """Techniques are the domain root's own synonyms, so they must resolve to
    the domain root's own CURIE -- if one drifts to another concept the
    generator's synonym walk has gone wrong."""
    domain_curie = INDEX["metabarcoding"]
    for slug in _edam.techniques():
        assert _edam.lookup(slug.replace("-", " ")) == domain_curie, slug


def test_the_domain_root_is_not_listed_as_its_own_subtopic():
    assert "metabarcoding" not in _edam.subtopics()


def test_subdomains_and_techniques_do_not_overlap():
    assert set(_edam.subtopics()).isdisjoint(_edam.techniques())


def test_size_reports_the_whole_index():
    assert _edam.size() == len(INDEX)
