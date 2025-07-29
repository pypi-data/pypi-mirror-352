"""
Test helpers for StarLive framework testing.

This module provides utilities for testing StarLive functionality across
both Starlette and FastAPI frameworks, reducing code duplication in tests.
"""

from typing import Optional

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

from starlive import StarLive, StarLiveMiddleware


def create_test_starlette_app(starlive: StarLive) -> Starlette:
    """Create a Starlette test app with StarLive."""

    async def homepage(request: Request):
        return HTMLResponse("Hello World")

    async def test_endpoint(request: Request):
        if request.state.can_stream():
            content = '<div class="updated">Content updated</div>'
            stream = starlive.update(
                content, "#target", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(stream, request.state.hypermedia_type)
        return HTMLResponse("Updated")

    async def complex_endpoint(request: Request):
        """Test endpoint with multiple operations."""
        if request.state.can_stream():
            streams = [
                starlive.append(
                    "<div>New item</div>",
                    "#items",
                    hypermedia_type=request.state.hypermedia_type,
                ),
                starlive.update(
                    "<div>Status: Updated</div>",
                    "#status",
                    hypermedia_type=request.state.hypermedia_type,
                ),
            ]
            return starlive.stream(streams, request.state.hypermedia_type)
        return HTMLResponse("Complex operation completed")

    app = Starlette(
        routes=[
            Route("/", homepage),
            Route("/test", test_endpoint, methods=["POST"]),
            Route("/complex", complex_endpoint, methods=["POST"]),
        ]
    )

    # Add StarLive middleware and WebSocket route
    app.add_middleware(StarLiveMiddleware, starlive=starlive)
    app.router.routes.append(starlive.create_websocket_route())
    return app


def create_test_fastapi_app(starlive: StarLive) -> "FastAPI":
    """Create a FastAPI test app with StarLive."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")

    app = FastAPI()

    @app.get("/")
    async def homepage(request: FastAPIRequest):
        return FastAPIHTMLResponse("Hello World")

    @app.post("/test")
    async def test_endpoint(request: FastAPIRequest):
        if request.state.can_stream():
            content = '<div class="updated">Content updated</div>'
            stream = starlive.update(
                content, "#target", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(stream, request.state.hypermedia_type)
        return FastAPIHTMLResponse("Updated")

    @app.post("/complex")
    async def complex_endpoint(request: FastAPIRequest):
        """Test endpoint with multiple operations."""
        if request.state.can_stream():
            streams = [
                starlive.append(
                    "<div>New item</div>",
                    "#items",
                    hypermedia_type=request.state.hypermedia_type,
                ),
                starlive.update(
                    "<div>Status: Updated</div>",
                    "#status",
                    hypermedia_type=request.state.hypermedia_type,
                ),
            ]
            return starlive.stream(streams, request.state.hypermedia_type)
        return FastAPIHTMLResponse("Complex operation completed")

    # Add StarLive middleware
    app.add_middleware(StarLiveMiddleware, starlive=starlive)

    # Add WebSocket route for StarLive
    @app.websocket(starlive.ws_route)
    async def websocket_endpoint(websocket):
        await starlive._websocket_endpoint(websocket)

    return app


@pytest.fixture(params=["starlette", "fastapi"])
def test_app_with_framework(request):
    """Parametrized fixture for testing both frameworks."""
    framework = request.param

    if framework == "fastapi" and not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")

    starlive = StarLive()

    if framework == "starlette":
        app = create_test_starlette_app(starlive)
        client = TestClient(app)
    else:  # fastapi
        app = create_test_fastapi_app(starlive)
        client = FastAPITestClient(app)

    return {
        "framework": framework,
        "app": app,
        "client": client,
        "starlive": starlive,
    }


@pytest.fixture
def starlette_test_app():
    """Create a test Starlette app for framework-specific tests."""
    starlive = StarLive()
    app = create_test_starlette_app(starlive)
    return {"app": app, "starlive": starlive, "client": TestClient(app)}


@pytest.fixture
def fastapi_test_app():
    """Create a test FastAPI app for framework-specific tests."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")

    starlive = StarLive()
    app = create_test_fastapi_app(starlive)
    return {"app": app, "starlive": starlive, "client": FastAPITestClient(app)}


class TestAssertions:
    """Common test assertions for both frameworks."""

    @staticmethod
    def assert_hypermedia_response(
        response, expected_content_type: Optional[str] = None
    ):
        """Assert that response is a valid hypermedia response."""
        assert response.status_code == 200
        if expected_content_type:
            assert expected_content_type in response.headers.get("content-type", "")

    @staticmethod
    def assert_htmx_response(response):
        """Assert that response is a valid HTMX response."""
        TestAssertions.assert_hypermedia_response(response, "text/html")
        assert "updated" in response.text.lower()

    @staticmethod
    def assert_turbo_response(response):
        """Assert that response is a valid Turbo Stream response."""
        TestAssertions.assert_hypermedia_response(response)
        assert "turbo-stream" in response.text

    @staticmethod
    def assert_websocket_route_exists(app, starlive: StarLive):
        """Assert that WebSocket route exists in the application."""
        if hasattr(app, "router"):  # Starlette
            routes = [route.path for route in app.router.routes]
        else:  # FastAPI
            routes = [route.path for route in app.routes]

        assert starlive.ws_route in routes

    @staticmethod
    def assert_middleware_configured(app):
        """Assert that StarLive middleware is properly configured."""
        middleware_found = False

        if hasattr(app, "middleware_stack"):  # Starlette
            # Check if middleware is in the middleware stack
            middleware = app.middleware_stack
            while middleware is not None:
                middleware_name = type(middleware).__name__
                if "StarLive" in middleware_name:
                    middleware_found = True
                    break
                # Check if it has a cls attribute (for middleware wrappers)
                if hasattr(middleware, "cls") and hasattr(middleware.cls, "__name__"):
                    if "StarLive" in middleware.cls.__name__:
                        middleware_found = True
                        break
                # Move to next middleware in stack
                middleware = getattr(middleware, "app", None)
        else:  # FastAPI
            for m in getattr(app, "user_middleware", []):
                if hasattr(m, "cls") and "StarLive" in m.cls.__name__:
                    middleware_found = True
                    break

        assert middleware_found, "StarLive middleware not found in application"


def run_framework_test(test_func, framework_name: Optional[str] = None):
    """
    Run a test function for specific framework(s).

    Args:
        test_func: Test function to run
        framework_name: "starlette", "fastapi", or None for both
    """
    frameworks = []

    if framework_name is None:
        frameworks = ["starlette"]
        if FASTAPI_AVAILABLE:
            frameworks.append("fastapi")
    elif framework_name == "fastapi" and not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    else:
        frameworks = [framework_name]

    for framework in frameworks:
        starlive = StarLive()

        if framework == "starlette":
            app = create_test_starlette_app(starlive)
            client = TestClient(app)
        else:
            app = create_test_fastapi_app(starlive)
            client = FastAPITestClient(app)

        test_context = {
            "framework": framework,
            "app": app,
            "client": client,
            "starlive": starlive,
        }

        test_func(test_context)
