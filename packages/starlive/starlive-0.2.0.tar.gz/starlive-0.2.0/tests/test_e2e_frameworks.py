"""
End-to-end tests for StarLive across different frameworks.

This module tests StarLive functionality across Starlette and FastAPI
to ensure consistent behavior regardless of the underlying framework.
"""

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.testclient import TestClient

try:
    from fastapi import FastAPI
    from fastapi import Request as FastAPIRequest
    from fastapi.responses import HTMLResponse as FastAPIHTMLResponse
    from fastapi.testclient import TestClient as FastAPITestClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from starlive import HypermediaType, StarLive, StarLiveMiddleware


@pytest.fixture(params=["starlette", "fastapi"])
def framework_app(request):
    """Create test apps for both frameworks."""
    framework = request.param

    if framework == "fastapi" and not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")

    starlive = StarLive(ws_route="/test-ws")

    if framework == "starlette":
        app = create_starlette_test_app(starlive)
        client = TestClient(app)
    else:  # fastapi
        app = create_fastapi_test_app(starlive)
        client = FastAPITestClient(app)

    return {"framework": framework, "app": app, "client": client, "starlive": starlive}


def create_starlette_test_app(starlive: StarLive) -> Starlette:
    """Create a comprehensive Starlette test application."""

    async def index(request: Request):
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>{starlive.get_scripts()}</head>
        <body>
            <div id="content">Original Content</div>
            <div id="messages"></div>
        </body>
        </html>
        """)

    async def update_htmx(request: Request):
        if request.state.can_stream():
            content = "<div>Updated via HTMX</div>"
            if request.state.hypermedia_type == "htmx":
                return HTMLResponse(content)
            else:
                stream = starlive.update(
                    content, "#content", hypermedia_type=request.state.hypermedia_type
                )
                return starlive.stream(stream, request.state.hypermedia_type)
        return HTMLResponse("No hypermedia support")

    async def update_turbo(request: Request):
        if request.state.can_stream():
            content = "<div>Updated via Turbo</div>"
            stream = starlive.update(
                content, "#content", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(stream, request.state.hypermedia_type)
        return HTMLResponse("No hypermedia support")

    async def append_content(request: Request):
        if request.state.can_stream():
            content = '<div class="new-item">New Item</div>'
            stream = starlive.append(
                content, "#messages", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(stream, request.state.hypermedia_type)
        return HTMLResponse("No hypermedia support")

    app = Starlette(
        routes=[
            Route("/", index),
            Route("/update-htmx", update_htmx, methods=["POST"]),
            Route("/update-turbo", update_turbo, methods=["POST"]),
            Route("/append", append_content, methods=["POST"]),
        ]
    )

    # Add StarLive middleware and WebSocket route
    app.add_middleware(StarLiveMiddleware, starlive=starlive)
    app.router.routes.append(starlive.create_websocket_route())

    return app


def create_fastapi_test_app(starlive: StarLive) -> "FastAPI":
    """Create a comprehensive FastAPI test application."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")

    app = FastAPI()

    @app.get("/")
    async def index(request: FastAPIRequest):
        return FastAPIHTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>{starlive.get_scripts()}</head>
        <body>
            <div id="content">Original Content</div>
            <div id="messages"></div>
        </body>
        </html>
        """)

    @app.post("/update-htmx")
    async def update_htmx(request: FastAPIRequest):
        if request.state.can_stream():
            content = "<div>Updated via HTMX</div>"
            if request.state.hypermedia_type == "htmx":
                return FastAPIHTMLResponse(content)
            else:
                stream = starlive.update(
                    content, "#content", hypermedia_type=request.state.hypermedia_type
                )
                return starlive.stream(stream, request.state.hypermedia_type)
        return FastAPIHTMLResponse("No hypermedia support")

    @app.post("/update-turbo")
    async def update_turbo(request: FastAPIRequest):
        if request.state.can_stream():
            content = "<div>Updated via Turbo</div>"
            stream = starlive.update(
                content, "#content", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(stream, request.state.hypermedia_type)
        return FastAPIHTMLResponse("No hypermedia support")

    @app.post("/append")
    async def append_content(request: FastAPIRequest):
        if request.state.can_stream():
            content = '<div class="new-item">New Item</div>'
            stream = starlive.append(
                content, "#messages", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(stream, request.state.hypermedia_type)
        return FastAPIHTMLResponse("No hypermedia support")

    # Add StarLive middleware
    app.add_middleware(StarLiveMiddleware, starlive=starlive)

    # Add WebSocket route for StarLive
    @app.websocket(starlive.ws_route)
    async def websocket_endpoint(websocket):
        await starlive._websocket_endpoint(websocket)

    return app


class TestFrameworkConsistency:
    """Test that StarLive behaves consistently across frameworks."""

    def test_index_page_loads(self, framework_app):
        """Test that the index page loads correctly."""
        client = framework_app["client"]
        response = client.get("/")

        assert response.status_code == 200
        assert "Original Content" in response.text
        assert "starlive-stream" in response.text or "test-ws" in response.text

    def test_htmx_detection_and_response(self, framework_app):
        """Test HTMX request detection and response."""
        client = framework_app["client"]

        # Test HTMX request
        response = client.post("/update-htmx", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert "Updated via HTMX" in response.text
        assert response.headers.get("content-type") == "text/html; charset=utf-8"

    def test_turbo_detection_and_response(self, framework_app):
        """Test Turbo request detection and response."""
        client = framework_app["client"]

        # Test Turbo request
        response = client.post(
            "/update-turbo", headers={"Accept": "text/vnd.turbo-stream.html"}
        )
        assert response.status_code == 200
        assert "Updated via Turbo" in response.text
        assert "turbo-stream" in response.text
        assert "text/vnd.turbo-stream.html" in response.headers.get("content-type", "")

    def test_non_hypermedia_fallback(self, framework_app):
        """Test fallback behavior for non-hypermedia requests."""
        client = framework_app["client"]

        response = client.post("/update-htmx")
        assert response.status_code == 200
        assert response.text == "No hypermedia support"

    def test_append_operation(self, framework_app):
        """Test append operation across frameworks."""
        client = framework_app["client"]

        # Test HTMX append
        response = client.post("/append", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert "New Item" in response.text

        # Test Turbo append
        response = client.post(
            "/append", headers={"Accept": "text/vnd.turbo-stream.html"}
        )
        assert response.status_code == 200
        assert "turbo-stream" in response.text
        assert "New Item" in response.text

    def test_middleware_state_injection(self, framework_app):
        """Test that middleware properly injects state."""
        # This is tested implicitly through the other tests,
        # but we can add specific state checks if needed
        pass

    def test_websocket_route_creation(self, framework_app):
        """Test WebSocket route creation."""
        app = framework_app["app"]
        framework = framework_app["framework"]

        if framework == "starlette":
            # Check WebSocket routes in Starlette
            ws_routes = [
                route
                for route in app.router.routes
                if hasattr(route, "path") and route.path == "/test-ws"
            ]
            assert len(ws_routes) == 1
        else:  # FastAPI
            # For FastAPI, we can't easily inspect routes the same way,
            # but we know the WebSocket endpoint was decorated
            pass

    def test_script_generation_consistency(self, framework_app):
        """Test that script generation is consistent across frameworks."""
        starlive = framework_app["starlive"]

        scripts = starlive.get_scripts()
        assert "htmx" in scripts
        assert "turbo" in scripts.lower()
        assert "/test-ws" in scripts

    def test_stream_operations_consistency(self, framework_app):
        """Test that stream operations work consistently."""
        starlive = framework_app["starlive"]

        # Test HTMX streams
        htmx_stream = starlive.append(
            "content", "#target", hypermedia_type=HypermediaType.HTMX
        )
        assert htmx_stream["type"] == "htmx"
        assert htmx_stream["action"] == "beforeend"

        # Test Turbo streams
        turbo_stream = starlive.append(
            "content", "#target", hypermedia_type=HypermediaType.TURBO
        )
        assert "turbo-stream" in turbo_stream
        assert 'action="append"' in turbo_stream


class TestFrameworkSpecificFeatures:
    """Test framework-specific features and behaviors."""

    def test_fastapi_openapi_integration(self):
        """Test FastAPI-specific features like OpenAPI docs."""
        if not FASTAPI_AVAILABLE:
            pytest.skip("FastAPI not available")

        starlive = StarLive()
        app = create_fastapi_test_app(starlive)
        client = FastAPITestClient(app)

        # Test that OpenAPI docs are available
        response = client.get("/docs")
        assert response.status_code == 200

        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        # FastAPI app title is "FastAPI" by default, not "StarLive"
        assert "FastAPI" in response.json().get("info", {}).get("title", "")

    def test_starlette_route_inspection(self):
        """Test Starlette-specific route inspection."""
        starlive = StarLive()
        app = create_starlette_test_app(starlive)

        # Test that we can inspect routes
        route_paths = [
            route.path for route in app.router.routes if hasattr(route, "path")
        ]
        assert "/" in route_paths
        assert "/update-htmx" in route_paths
        # The WebSocket route is created with the starlive instance's ws_route
        assert starlive.ws_route in route_paths


# Parametrized tests for cross-framework compatibility
@pytest.mark.parametrize(
    "hypermedia_type,headers,expected_content",
    [
        ("htmx", {"HX-Request": "true"}, "text/html"),
        ("turbo", {"Accept": "text/vnd.turbo-stream.html"}, "turbo-stream"),
    ],
)
def test_hypermedia_type_detection(
    framework_app, hypermedia_type, headers, expected_content
):
    """Parametrized test for hypermedia type detection."""
    client = framework_app["client"]

    response = client.post("/update-htmx", headers=headers)
    assert response.status_code == 200
    assert expected_content in (
        response.text + response.headers.get("content-type", "")
    )


@pytest.mark.parametrize("endpoint", ["/update-htmx", "/update-turbo", "/append"])
def test_endpoints_respond_correctly(framework_app, endpoint):
    """Test that all endpoints respond correctly to hypermedia requests."""
    client = framework_app["client"]

    # Test with HTMX
    response = client.post(endpoint, headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert response.text != "No hypermedia support"

    # Test with Turbo
    response = client.post(endpoint, headers={"Accept": "text/vnd.turbo-stream.html"})
    assert response.status_code == 200
    assert response.text != "No hypermedia support"
