"""
StarLive - Universal Hypermedia System for Starlette & FastAPI

A unified interface for both HTMX and Turbo hypermedia systems with real-time capabilities.
"""

import uuid
from typing import Callable, List, Optional, Union

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket

from .detection import HypermediaDetector
from .scripts import ScriptGenerator
from .streams import StreamGenerator
from .types import HypermediaType, StreamContent
from .websocket import WebSocketManager

# Re-export commonly used types and constants
__all__ = [
    "HypermediaType",
    "StarLive",
    "StarLiveMiddleware",
    "starlive_context_processor",
]


class StarLive:
    """Main StarLive application class for hypermedia integration."""

    def __init__(
        self, app: Optional[Starlette] = None, ws_route: str = "/starlive-stream"
    ):
        self.ws_route = ws_route
        self.user_id_callback: Callable[[], str] = self._default_user_id

        # Initialize components
        self._websocket_manager = WebSocketManager(self.user_id_callback)
        self._script_generator = ScriptGenerator(ws_route)
        self._stream_generator = StreamGenerator()
        self._detector = HypermediaDetector()

        if app:
            self.init_app(app)

    def init_app(self, app: Starlette) -> None:
        """Initialize StarLive with a Starlette application."""
        # Add WebSocket route for real-time updates
        websocket_route = WebSocketRoute(self.ws_route, self._websocket_endpoint)
        app.router.routes.append(websocket_route)

        # Add middleware to detect hypermedia type and inject context
        app.add_middleware(StarLiveMiddleware, starlive=self)

    async def _websocket_endpoint(self, websocket: WebSocket) -> None:
        """WebSocket endpoint handler."""
        await self._websocket_manager.handle_connection(websocket)

    def user_id(self, f: Callable[[], str]) -> Callable[[], str]:
        """Configure an application-specific user id generator."""
        self.user_id_callback = f
        self._websocket_manager.user_id_callback = f
        return f

    def _default_user_id(self) -> str:
        """Default user id generator."""
        return uuid.uuid4().hex

    # Hypermedia detection methods
    def detect_hypermedia_type(self, request: Request) -> str:
        """Detect whether the client prefers HTMX or Turbo."""
        return self._detector.detect_hypermedia_type(request)

    def can_stream(self, request: Request) -> bool:
        """Returns True if the client accepts streaming responses."""
        return self._detector.can_stream(request)

    def can_push(self, to: Optional[str] = None) -> bool:
        """Returns True if the client accepts real-time updates over WebSocket."""
        return self._websocket_manager.can_push(to)

    # Script generation methods
    def get_scripts(
        self,
        hypermedia_type: Optional[str] = None,
        turbo_version: Optional[str] = None,
        htmx_version: Optional[str] = None,
        turbo_url: Optional[str] = None,
        htmx_url: Optional[str] = None,
    ) -> str:
        """Generate script tags for the hypermedia library."""
        return self._script_generator.get_scripts(
            hypermedia_type=hypermedia_type,
            turbo_version=turbo_version
            or self._script_generator.get_default_turbo_version(),
            htmx_version=htmx_version
            or self._script_generator.get_default_htmx_version(),
            turbo_url=turbo_url,
            htmx_url=htmx_url,
        )

    # Stream generation methods - delegate to StreamGenerator
    def append(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> Union[str, dict]:
        """Create an append/afterend stream."""
        return self._stream_generator.append(content, target, multiple, hypermedia_type)

    def prepend(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> Union[str, dict]:
        """Create a prepend/afterbegin stream."""
        return self._stream_generator.prepend(
            content, target, multiple, hypermedia_type
        )

    def replace(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> Union[str, dict]:
        """Create a replace/outerHTML stream."""
        return self._stream_generator.replace(
            content, target, multiple, hypermedia_type
        )

    def update(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> Union[str, dict]:
        """Create an update/innerHTML stream."""
        return self._stream_generator.update(content, target, multiple, hypermedia_type)

    def remove(
        self, target: str, multiple: bool = False, hypermedia_type: Optional[str] = None
    ) -> Union[str, dict]:
        """Create a remove/delete stream."""
        return self._stream_generator.remove(target, multiple, hypermedia_type)

    def after(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> Union[str, dict]:
        """Create an after/afterend stream."""
        return self._stream_generator.after(content, target, multiple, hypermedia_type)

    def before(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> Union[str, dict]:
        """Create a before/beforebegin stream."""
        return self._stream_generator.before(content, target, multiple, hypermedia_type)

    def stream(
        self, stream: StreamContent, hypermedia_type: Optional[str] = None
    ) -> Response:
        """Create a hypermedia stream response."""
        if hypermedia_type == HypermediaType.HTMX:
            # For HTMX, we typically return HTML directly
            if isinstance(stream, dict):
                content = stream.get("content", "")
            elif isinstance(stream, list):
                content = "".join(
                    s.get("content", "") if isinstance(s, dict) else str(s)
                    for s in stream
                )
            else:
                content = str(stream)
            return HTMLResponse(content)
        else:  # Turbo
            if isinstance(stream, list):
                content = "".join(str(s) for s in stream)
            else:
                content = str(stream)
            return Response(content, media_type="text/vnd.turbo-stream.html")

    async def push(
        self, stream: StreamContent, to: Optional[Union[str, List[str]]] = None
    ) -> None:
        """Push a stream update over WebSocket to one or more clients."""
        await self._websocket_manager.push(stream, to)


class StarLiveMiddleware(BaseHTTPMiddleware):
    """Middleware to inject StarLive context into requests."""

    def __init__(self, app, starlive: StarLive):
        super().__init__(app)
        self.starlive = starlive

    async def dispatch(self, request: Request, call_next):
        """Add StarLive context to the request state."""
        # Detect hypermedia type and add to request state
        hypermedia_type = self.starlive.detect_hypermedia_type(request)
        request.state.hypermedia_type = hypermedia_type
        request.state.starlive = self.starlive

        # Add convenience methods to request state
        request.state.can_stream = lambda: self.starlive.can_stream(request)
        request.state.requested_frame = lambda: request.headers.get("Turbo-Frame", "")
        request.state.is_htmx = lambda: "HX-Request" in request.headers
        request.state.htmx_target = lambda: request.headers.get("HX-Target", "")
        request.state.htmx_trigger = lambda: request.headers.get("HX-Trigger", "")
        request.state.is_turbo = lambda: self.starlive._detector.is_turbo_request(
            request
        )

        response = await call_next(request)
        return response


def starlive_context_processor(starlive: StarLive):
    """Template context processor for Jinja2."""

    def processor():
        return {"starlive_scripts": starlive.get_scripts, "starlive": starlive}

    return processor
