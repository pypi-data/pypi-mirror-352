"""
Data models used by the EUVD service.
"""

from .customfieldtypes import (
    EUVDIdType,
    BaseScoreValueType,
    EPSSScoreValueType,
)
from .basescore import BaseScore

from .enisavulnerability import EnisaVulnerability

from .vulnerability import Vulnerability
from .advisory import Advisory

from .product import Product
from .vendor import Vendor
from .source import Source

from .enisaidenisavulnerabilityref import EnisaIdEnisaVulnerabilityRef
from .enisaidvulnerabilityref import EnisaIdVulnerabilityRef
from .enisaidproductref import EnisaIdProductRef
from .enisaidvendorref import EnisaIdVendorRef

from .pagination import Pagination
