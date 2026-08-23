"""Hardcoded CURIE prefix to base-IRI table for the metabarcoding adapter.

Nothing here is fetched at runtime: every expansion is pinned in this file, so
changing one changes how every metabarcoding claim CURIE expands downstream.

This table only *expands* identifiers and accessions that some other component
already recognised in text -- it never recognises one itself. SILVA accessions,
UNITE species-hypothesis identifiers and BOLD process ids in particular are
recognised by ``asb-domain-core``, not here; a second detection table in this
package would be the duplicate-then-drift failure ADR 0001 exists to prevent.

Two families:

* **Ontology prefixes** -- NCBITaxon, ENVO, OBI and EDAM are the vocabularies
  claim text is resolved against. Expansions are OBO PURLs, or the ontology's
  own base IRI where it is not an OBO library member (EDAM).
* **Reference-database and repository prefixes** -- SILVA, UNITE, BOLD, ENA and
  MIxS are the databases a metabarcoding paper cites without this package
  attempting to resolve claim text against them: a taxonomy, marker-gene or
  checklist database is not itself a controlled label vocabulary the way an
  ontology is. Their entries exist so a consumer can expand a CURIE some other
  component minted.

``edam`` is lower-case on purpose: it is the prefix ``_edam.py`` mints into
every CURIE it returns, matching the sibling genomics and proteomics adapters.
"""

from __future__ import annotations

from typing import Final

# --- Ontologies ---------------------------------------------------------------

NCBITAXON: Final[str] = "http://purl.obolibrary.org/obo/NCBITaxon_"
ENVO: Final[str] = "http://purl.obolibrary.org/obo/ENVO_"
OBI: Final[str] = "http://purl.obolibrary.org/obo/OBI_"
# Lower-case on purpose: it is the prefix `_edam.py` mints into every CURIE it
# returns, and `test_edam_index.py` binds the two together so they cannot drift.
EDAM: Final[str] = "http://edamontology.org/"

# --- Reference databases and repositories --------------------------------------

# UNITE is registered with identifiers.org (MIR:00000352); its compact-URI
# resolver expands both the UDB accession form and the SH species-hypothesis
# form it publishes.
UNITE: Final[str] = "https://identifiers.org/unite:"
# SILVA has no identifiers.org registration; its own browser resolves an INSDC
# accession directly.
SILVA: Final[str] = "https://www.arb-silva.de/browser/ssu/silva/"
# BOLD process ids resolve through the public record view on the BOLD website.
BOLD: Final[str] = "http://www.boldsystems.org/index.php/Public_RecordView?processid="
# ENA accessions (the INSDC member a metabarcoding submission typically cites),
# via the same identifiers.org resolver the genomics adapter uses.
ENA: Final[str] = "https://identifiers.org/ena.embl:"
# MIxS (Minimum Information about any (x) Sequence) checklist terms are
# published by the Genomic Standards Consortium under a w3id.org PURL.
MIXS: Final[str] = "https://w3id.org/mixs/"


METABARCODING_PREFIXES: Final[dict[str, str]] = {
    # Ontologies.
    "NCBITaxon": NCBITAXON,
    "ENVO": ENVO,
    "OBI": OBI,
    "edam": EDAM,
    # Reference databases and repositories.
    "SILVA": SILVA,
    "UNITE": UNITE,
    "BOLD": BOLD,
    "ENA": ENA,
    "MIxS": MIXS,
}
