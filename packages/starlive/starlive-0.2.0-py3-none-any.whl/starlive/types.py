"""Type definitions and constants for StarLive."""

from enum import Enum
from typing import Dict, List, Optional, Union

from starlette.websockets import WebSocket


class HypermediaType(str, Enum):
    """Supported hypermedia types."""

    TURBO = "turbo"
    HTMX = "htmx"


class CDNConfig:
    """CDN configuration for hypermedia libraries."""

    # Turbo configuration
    TURBO_CDN = "https://cdn.jsdelivr.net"
    TURBO_PKG = "@hotwired/turbo"
    TURBO_VER = "8.0.11"

    # HTMX configuration
    HTMX_CDN = "https://unpkg.com"
    HTMX_PKG = "htmx.org"
    HTMX_VER = "2.0.3"


# Type aliases
StreamContent = Union[str, dict, List[Union[str, dict]]]
ClientRegistry = Dict[str, List[WebSocket]]
UserIdType = Optional[str]
