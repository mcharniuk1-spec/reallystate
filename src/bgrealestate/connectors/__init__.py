"""Source connectors (discovery + fetch + parse) live here.

Connectors must enforce the source registry legal/risk/access gates and must
not introduce live-network dependencies in unit tests (use fixtures).
"""

from .factory import build_connector, is_marketplace_source, marketplace_sources
from .legal import DerivedLegalRule, LegalGateError, assert_live_http_allowed, derive_default_legal_rule
from .scaffold import HtmlPortalConnector

__all__ = [
    "HtmlPortalConnector",
    "LegalGateError",
    "DerivedLegalRule",
    "assert_live_http_allowed",
    "derive_default_legal_rule",
    "build_connector",
    "is_marketplace_source",
    "marketplace_sources",
]
