"""Vendored EDAM label index -- the concept spine for the metabarcoding adapter.

Generated offline from EDAM by ``data/build_edam_index.py`` and shipped as a
package resource, so enrichment is a pure function with no network call at
runtime. ``data/edam_index.json`` records the ontology roots the index was cut
from, the subdomain and technique slugs read off the same walk, and the label
map itself.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Final

EDAM_PREFIX: Final[str] = "http://edamontology.org/"


@lru_cache(maxsize=1)
def _payload() -> dict:
    raw = files("indicium_adapters_metabarcoding.data").joinpath("edam_index.json").read_text()
    return json.loads(raw)


def _normalise(text: str) -> str:
    """Case-fold and collapse whitespace so lookup is punctuation-stable."""
    return " ".join(str(text).lower().split())


def lookup(text: str) -> str | None:
    """Return the EDAM CURIE for ``text``, or None when it names no EDAM concept.

    Matching is exact after normalisation. Substring matching over an ontology
    manufactures confident-looking wrong CURIEs ("Taxonomy" inside "Molecular
    taxonomy"), and a wrong identifier is worse than no identifier.
    """
    return _payload()["index"].get(_normalise(text))


def roots() -> tuple[str, ...]:
    """The EDAM classes this index was cut from -- provenance for the vocabulary."""
    return tuple(_payload()["roots"])


def subtopics() -> tuple[str, ...]:
    """Kebab-case slugs of the additional-root labels the index carries.

    The domain root, Metabarcoding, is a leaf in EDAM with no children of its
    own, so this list is what the walk actually found beyond it: the labels of
    Taxonomy, Phylogenetics and Microbial ecology, the three fields a
    metabarcoding paper draws on that EDAM does not file underneath it."""
    return tuple(_payload()["subtopics"])


def techniques() -> tuple[str, ...]:
    """Kebab-case slugs of the domain root's own EDAM-recorded synonyms.

    Metabarcoding has no child topics to supply a technique layer distinct from
    ``subtopics()``, but EDAM itself records five named variants of the practice
    as exact synonyms of the domain root (DNA, RNA, environmental, eDNA, eRNA
    metabarcoding). Those synonyms are read here rather than hand-listed."""
    return tuple(_payload()["techniques"])


def size() -> int:
    """Number of label/synonym entries in the index."""
    return len(_payload()["index"])
