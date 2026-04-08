"""Source connectors (discovery + fetch + parse) live here.

Connectors must enforce the source registry legal/risk/access gates and must
not introduce live-network dependencies in unit tests (use fixtures).
"""

from .factory import build_connector, is_marketplace_source, marketplace_sources
from .legal import DerivedLegalRule, LegalGateError, assert_live_http_allowed, derive_default_legal_rule
from .scaffold import HtmlPortalConnector
from .social_parser import extract_social_lead
from .tier3 import (
    BcpeaAuctionConnector,
    BcpeaDiscoveryItem,
    BcpeaDiscoveryPage,
    LicensedStrDataConnector,
    OfficialRegisterWrapper,
    OperatorConsentRequired,
    PartnerContractRequired,
    PartnerFeedStubConnector,
    parse_bcpea_detail_html,
    parse_bcpea_discovery_html,
)

__all__ = [
    "HtmlPortalConnector",
    "LegalGateError",
    "DerivedLegalRule",
    "assert_live_http_allowed",
    "derive_default_legal_rule",
    "build_connector",
    "extract_social_lead",
    "is_marketplace_source",
    "marketplace_sources",
    "PartnerFeedStubConnector",
    "PartnerContractRequired",
    "LicensedStrDataConnector",
    "OfficialRegisterWrapper",
    "OperatorConsentRequired",
    "BcpeaAuctionConnector",
    "BcpeaDiscoveryItem",
    "BcpeaDiscoveryPage",
    "parse_bcpea_discovery_html",
    "parse_bcpea_detail_html",
]
