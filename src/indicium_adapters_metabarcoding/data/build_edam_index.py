"""Maintainer script: regenerate ``edam_index.json`` from EDAM via EBI OLS4.

The index is the label spine ``_edam.py`` matches claim text against. It is cut
from a recorded set of EDAM roots: each root contributes itself and its direct
subclasses, and each of those contributes its preferred label plus every exact
synonym EDAM records. Nothing is hand-added -- a label that EDAM does not carry
resolves to a CURIE EDAM never issued, which is the wrong-CURIE failure the
whole package is built to avoid.

Usage (never run at install or import time)::

    python -m indicium_adapters_metabarcoding.data.build_edam_index

Re-run on an EDAM release. The roots below are the only vocabulary decision in
the file; everything else is read from EDAM.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Final

OLS_TERMS_URL: Final[str] = "https://www.ebi.ac.uk/ols4/api/ontologies/edam/terms"

EDAM_IRI_PREFIX: Final[str] = "http://edamontology.org/"

EDAM_CURIE_PREFIX: Final[str] = "edam"

# Metabarcoding. It names the domain itself, so it is the one collected term
# that is not also a subdomain of it. Confirmed against live EDAM (2026-08) to
# be a leaf topic -- it has no children of its own.
DOMAIN_ROOT: Final[str] = f"{EDAM_IRI_PREFIX}topic_4038"

# Taxonomy, Phylogenetics, Microbial ecology: a metabarcoding paper assigns
# taxonomy, builds a phylogenetic tree and reports community composition, but
# EDAM does not file any of the three underneath Metabarcoding. The
# relationship actually runs the other way for one of them -- Metabarcoding is
# the sole child of Microbial ecology -- and Taxonomy and Phylogenetics are
# themselves leaves with no children of their own, so walking from any of the
# three reaches nothing beyond the four root labels. Each is named explicitly
# so the index reaches them at all; see ``_techniques_of`` for how the index
# still produces a technique layer distinct from these subdomains despite that
# shallowness.
ADDITIONAL_ROOTS: Final[tuple[str, ...]] = (
    f"{EDAM_IRI_PREFIX}topic_0637",  # Taxonomy
    f"{EDAM_IRI_PREFIX}topic_3293",  # Phylogenetics
    f"{EDAM_IRI_PREFIX}topic_3697",  # Microbial ecology
)

ROOTS: Final[tuple[str, ...]] = (DOMAIN_ROOT, *ADDITIONAL_ROOTS)

SOURCE: Final[str] = "EDAM (edamontology.org/EDAM.csv); entries verified against EBI OLS4"

CHILD_PAGE_SIZE: Final[int] = 200

REQUEST_TIMEOUT_SECONDS: Final[int] = 60


def _normalise(text: str) -> str:
    """Case-fold and collapse whitespace, matching ``_edam.lookup``'s key form."""
    return " ".join(str(text).lower().split())


def _fetch(url: str) -> dict:
    """GET ``url`` and return the decoded JSON body."""
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.load(response)


def _term(iri: str) -> dict:
    """Return the OLS4 term record for one EDAM ``iri``."""
    query = urllib.parse.urlencode({"iri": iri})
    terms = _fetch(f"{OLS_TERMS_URL}?{query}").get("_embedded", {}).get("terms", [])
    if not terms:
        raise RuntimeError(f"EDAM has no term {iri}")
    return terms[0]


def _children(term: dict) -> list[dict]:
    """Return the direct subclasses of ``term``, or [] when it is a leaf."""
    link = term["_links"].get("hierarchicalChildren", {}).get("href")
    if not link:
        return []
    page = _fetch(f"{link}?size={CHILD_PAGE_SIZE}")
    return page.get("_embedded", {}).get("terms", [])


def _entries(term: dict) -> dict[str, str]:
    """Map every label and exact synonym of ``term`` to its ``edam:`` CURIE."""
    local = term["iri"].removeprefix(EDAM_IRI_PREFIX)
    curie = f"{EDAM_CURIE_PREFIX}:{local}"
    names = [term["label"], *(term.get("synonyms") or [])]
    return {_normalise(name): curie for name in names if str(name).strip()}


def _slug(label: str) -> str:
    """Return ``label`` as the kebab-case slug the classification vocabulary uses."""
    return "-".join(_normalise(label).split())


def _collect(roots: tuple[str, ...]) -> list[dict]:
    """Return every EDAM term the index covers: each root and its direct subclasses."""
    terms: dict[str, dict] = {}
    for iri in roots:
        root = _term(iri)
        for term in (root, *_children(root)):
            terms.setdefault(term["iri"], term)
    return list(terms.values())


def _index_of(terms: list[dict]) -> dict[str, str]:
    """Map every label and exact synonym across ``terms`` to its ``edam:`` CURIE."""
    index: dict[str, str] = {}
    for term in terms:
        index.update(_entries(term))
    return dict(sorted(index.items()))


def _subtopics_of(terms: list[dict]) -> list[str]:
    """Return the preferred-label slug of every term except the domain root.

    This is the adapter's ``subdomains``: the fields the index actually reached
    beyond Metabarcoding itself -- Taxonomy, Phylogenetics and Microbial ecology,
    each contributing only its own label because none of the three has children
    either (see the module docstring)."""
    return sorted({_slug(term["label"]) for term in terms if term["iri"] != DOMAIN_ROOT})


def _techniques_of(terms: list[dict]) -> list[str]:
    """Return the domain root's own synonym slugs -- the adapter's ``techniques``.

    Metabarcoding has no child topics, so it cannot supply a technique layer the
    way ``_subtopics_of`` supplies subdomains from the additional roots. EDAM
    still records five named variants of the practice as exact synonyms of the
    domain root itself (DNA, RNA, environmental, eDNA and eRNA metabarcoding),
    and those are read here rather than curated by hand."""
    root = next(term for term in terms if term["iri"] == DOMAIN_ROOT)
    return sorted({_slug(name) for name in (root.get("synonyms") or [])})


def main() -> None:
    """Rebuild ``edam_index.json`` next to this script from :data:`ROOTS`."""
    terms = _collect(ROOTS)
    payload = {
        "index": _index_of(terms),
        "subtopics": _subtopics_of(terms),
        "techniques": _techniques_of(terms),
        "roots": list(ROOTS),
        "source": SOURCE,
    }
    target = Path(__file__).parent / "edam_index.json"
    target.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    print(f"[edam] wrote {target} with {len(payload['index']):,} entries", file=sys.stderr)


if __name__ == "__main__":
    main()
