"""Hypermedia type detection utilities."""

from starlette.requests import Request

from .types import HypermediaType


class HypermediaDetector:
    """Detects hypermedia types and capabilities from HTTP requests."""

    @staticmethod
    def detect_hypermedia_type(request: Request) -> str:
        """Detect whether the client prefers HTMX or Turbo."""
        # Check for HTMX-specific headers
        if "HX-Request" in request.headers:
            return HypermediaType.HTMX

        # Check for Turbo-specific headers or accept types
        if "Turbo-Frame" in request.headers:
            return HypermediaType.TURBO

        # Check accept headers for turbo stream
        accept = request.headers.get("accept", "")
        if "text/vnd.turbo-stream.html" in accept:
            return HypermediaType.TURBO

        # Default to HTMX if no specific indicators
        return HypermediaType.HTMX

    @staticmethod
    def can_stream(request: Request) -> bool:
        """Returns True if the client accepts streaming responses."""
        hypermedia_type = HypermediaDetector.detect_hypermedia_type(request)

        if hypermedia_type == HypermediaType.HTMX:
            return "HX-Request" in request.headers
        else:  # Turbo
            stream_mimetype = "text/vnd.turbo-stream.html"
            accept = request.headers.get("accept", "")
            return stream_mimetype in accept

    @staticmethod
    def is_htmx_request(request: Request) -> bool:
        """Check if the request was made by HTMX."""
        return "HX-Request" in request.headers

    @staticmethod
    def is_turbo_request(request: Request) -> bool:
        """Check if the request was made by Turbo."""
        return (
            "Turbo-Frame" in request.headers
            or "text/vnd.turbo-stream.html" in request.headers.get("accept", "")
        )

    @staticmethod
    def get_htmx_target(request: Request) -> str:
        """Get the HTMX target element ID."""
        return request.headers.get("HX-Target", "")

    @staticmethod
    def get_htmx_trigger(request: Request) -> str:
        """Get the HTMX triggering element ID."""
        return request.headers.get("HX-Trigger", "")

    @staticmethod
    def get_turbo_frame(request: Request) -> str:
        """Get the requested Turbo Frame ID."""
        return request.headers.get("Turbo-Frame", "")
