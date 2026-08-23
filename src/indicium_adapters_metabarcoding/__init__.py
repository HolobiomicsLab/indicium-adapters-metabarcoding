"""Metabarcoding DomainAdapter for the indicium ecosystem.

Exposes :class:`MetabarcodingAdapter` via the ``indicium.adapters`` entry point,
so ``indicium_adapters.discover_adapters()`` finds it on install and ASB's
classification vocabulary picks up ``primary_domain="metabarcoding"``.
"""

from .metabarcoding import MetabarcodingAdapter

__all__ = ["MetabarcodingAdapter", "__version__"]

__version__ = "0.1.0"
