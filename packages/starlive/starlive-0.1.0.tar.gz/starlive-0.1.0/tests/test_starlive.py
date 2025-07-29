import unittest

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from starlive import HypermediaType, StarLive, starlive_context_processor


@pytest.fixture
def starlive_app():
    """Create a test Starlette app with StarLive."""
    starlive = StarLive()

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

    app = Starlette(
        routes=[
            Route("/", homepage),
            Route("/test", test_endpoint, methods=["POST"]),
        ]
    )

    starlive.init_app(app)
    return app


def test_hypermedia_detection_htmx():
    """Test HTMX detection."""
    app = Starlette()
    starlive = StarLive(app)  # Initialize StarLive with app reference

    @app.route("/test", methods=["POST"])
    async def test_endpoint(request):
        if request.state.can_stream():
            content = '<div class="updated">Content updated</div>'
            stream = starlive.update(
                content, "#target", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(stream, request.state.hypermedia_type)
        return HTMLResponse("Updated")

    client = TestClient(app)
    response = client.post("/test", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert "updated" in response.text.lower()


def test_hypermedia_detection_turbo():
    """Test Turbo detection."""
    app = Starlette()
    starlive = StarLive(app)  # Initialize StarLive with app reference

    @app.route("/test", methods=["POST"])
    async def test_endpoint(request):
        if request.state.can_stream():
            content = '<div class="updated">Content updated</div>'
            stream = starlive.update(
                content, "#target", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(stream, request.state.hypermedia_type)
        return HTMLResponse("Updated")

    client = TestClient(app)
    response = client.post("/test", headers={"Accept": "text/vnd.turbo-stream.html"})
    assert response.status_code == 200
    assert "turbo-stream" in response.text


def test_hypermedia_detection_default():
    """Test default behavior without hypermedia headers."""
    app = Starlette()
    starlive = StarLive()

    @app.route("/test", methods=["POST"])
    async def test_endpoint(request):
        if request.state.can_stream():
            content = '<div class="updated">Content updated</div>'
            stream = starlive.update(
                content, "#target", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(stream, request.state.hypermedia_type)
        return HTMLResponse("Updated")

    starlive.init_app(app)

    client = TestClient(app)
    response = client.post("/test")
    assert response.status_code == 200
    assert response.text == "Updated"


def test_stream_operations():
    """Test stream generation methods."""
    starlive = StarLive()

    # Test HTMX streams
    htmx_append = starlive.append(
        "content", "#target", hypermedia_type=HypermediaType.HTMX
    )
    assert htmx_append["type"] == "htmx"
    assert htmx_append["action"] == "beforeend"
    assert htmx_append["target"] == "#target"
    assert htmx_append["content"] == "content"

    # Test Turbo streams
    turbo_append = starlive.append(
        "content", "#target", hypermedia_type=HypermediaType.TURBO
    )
    assert "turbo-stream" in turbo_append
    assert 'action="append"' in turbo_append
    assert 'target="#target"' in turbo_append


def test_script_generation():
    """Test script generation for different hypermedia types."""
    starlive = StarLive()

    # Test HTMX scripts
    htmx_scripts = starlive.get_scripts(hypermedia_type=HypermediaType.HTMX)
    assert "htmx" in htmx_scripts
    assert "unpkg.com" in htmx_scripts

    # Test Turbo scripts
    turbo_scripts = starlive.get_scripts(hypermedia_type=HypermediaType.TURBO)
    assert "turbo" in turbo_scripts.lower()
    assert "cdn.jsdelivr.net" in turbo_scripts

    # Test both scripts (default)
    both_scripts = starlive.get_scripts()
    assert "htmx" in both_scripts
    assert "turbo" in both_scripts.lower()


def test_websocket_route_generation():
    """Test WebSocket route generation in scripts."""
    custom_route = "/custom-stream"
    starlive = StarLive(ws_route=custom_route)

    scripts = starlive.get_scripts()
    assert custom_route in scripts


def test_can_push():
    """Test push capability detection."""
    starlive = StarLive()

    # No clients connected
    assert not starlive.can_push()
    assert not starlive.can_push("user123")

    # Simulate connected client by accessing internal manager
    starlive._websocket_manager.clients["user123"] = ["mock_websocket"]
    assert starlive.can_push()
    assert starlive.can_push("user123")
    assert not starlive.can_push("user456")


def test_user_id_callback():
    """Test custom user ID callback."""
    starlive = StarLive()

    @starlive.user_id
    def custom_user_id():
        return "custom_user_123"

    assert starlive.user_id_callback() == "custom_user_123"


def test_hypermedia_type_constants():
    """Test hypermedia type constants."""
    assert HypermediaType.HTMX == "htmx"
    assert HypermediaType.TURBO == "turbo"


class TestStarLive(unittest.TestCase):
    def test_direct_create(self):
        """Test direct StarLive creation with app."""
        app = Starlette()
        StarLive(app)

        @app.route("/test")
        async def test_route(request):
            return HTMLResponse("test")

        client = TestClient(app)
        response = client.get("/test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "test")

        # Check that WebSocket route was added
        ws_routes = [
            route
            for route in app.router.routes
            if hasattr(route, "path") and route.path == "/starlive-stream"
        ]
        self.assertEqual(len(ws_routes), 1)

    def test_indirect_create(self):
        """Test indirect StarLive creation without app."""
        app = Starlette()
        starlive = StarLive()

        @app.route("/test")
        async def test_route(request):
            return HTMLResponse("test")

        starlive.init_app(app)

        client = TestClient(app)
        response = client.get("/test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "test")

    def test_create_custom_ws_route(self):
        """Test StarLive creation with custom WebSocket route."""
        app = Starlette()
        starlive = StarLive(ws_route="/custom-ws")

        @app.route("/test")
        async def test_route(request):
            return HTMLResponse("test")

        starlive.init_app(app)

        # Check that custom WebSocket route was added
        ws_routes = [
            route
            for route in app.router.routes
            if hasattr(route, "path") and route.path == "/custom-ws"
        ]
        self.assertEqual(len(ws_routes), 1)

        # Check scripts contain custom route
        scripts = starlive.get_scripts()
        self.assertIn("/custom-ws", scripts)

    def test_create_custom_versions(self):
        """Test custom library versions."""
        starlive = StarLive()

        # Test custom Turbo version
        turbo_scripts = starlive.get_scripts(
            hypermedia_type=HypermediaType.TURBO, turbo_version="1.2.3"
        )
        assert b"@hotwired/turbo@1.2.3/dist" in turbo_scripts.encode()

        # Test custom HTMX version
        htmx_scripts = starlive.get_scripts(
            hypermedia_type=HypermediaType.HTMX, htmx_version="2.0.0"
        )
        assert b"htmx.org@2.0.0/dist" in htmx_scripts.encode()

    def test_create_custom_urls(self):
        """Test custom library URLs."""
        starlive = StarLive()

        # Test custom Turbo URL
        turbo_scripts = starlive.get_scripts(
            hypermedia_type=HypermediaType.TURBO, turbo_url="/js/turbo.js"
        )
        assert b"/js/turbo.js" in turbo_scripts.encode()

        # Test custom HTMX URL
        htmx_scripts = starlive.get_scripts(
            hypermedia_type=HypermediaType.HTMX, htmx_url="/js/htmx.js"
        )
        assert b"/js/htmx.js" in htmx_scripts.encode()

    def test_hypermedia_detection_htmx(self):
        """Test HTMX detection via middleware."""
        app = Starlette()
        StarLive(app)

        @app.route("/test", methods=["POST"])
        async def test_route(request):
            return HTMLResponse(request.state.hypermedia_type)

        client = TestClient(app)
        response = client.post("/test", headers={"HX-Request": "true"})
        assert response.text == "htmx"

    def test_hypermedia_detection_turbo(self):
        """Test Turbo detection via middleware."""
        app = Starlette()
        StarLive(app)

        @app.route("/test", methods=["POST"])
        async def test_route(request):
            return HTMLResponse(request.state.hypermedia_type)

        client = TestClient(app)
        response = client.post(
            "/test", headers={"Accept": "text/vnd.turbo-stream.html"}
        )
        assert response.text == "turbo"

    def test_requested_frame_turbo(self):
        """Test Turbo frame detection."""
        app = Starlette()
        StarLive(app)

        @app.route("/test")
        async def test_route(request):
            return HTMLResponse(request.state.requested_frame())

        client = TestClient(app)
        response = client.get("/test", headers={"Turbo-Frame": "my-frame"})
        assert response.text == "my-frame"

    def test_htmx_headers(self):
        """Test HTMX header detection."""
        app = Starlette()
        StarLive(app)

        @app.route("/test")
        async def test_route(request):
            return HTMLResponse(
                f"{request.state.htmx_target()},{request.state.htmx_trigger()}"
            )

        client = TestClient(app)
        response = client.get(
            "/test", headers={"HX-Target": "my-target", "HX-Trigger": "my-trigger"}
        )
        assert response.text == "my-target,my-trigger"

    def test_can_stream_detection(self):
        """Test stream capability detection."""
        app = Starlette()
        StarLive(app)

        @app.route("/test")
        async def test_route(request):
            return HTMLResponse(str(request.state.can_stream()))

        client = TestClient(app)

        # Test HTMX request (can stream)
        response = client.get("/test", headers={"HX-Request": "true"})
        assert response.text == "True"

        # Test regular request (cannot stream)
        response = client.get("/test")
        assert response.text == "False"

    def test_can_push(self):
        """Test push capability detection."""
        starlive = StarLive()

        # No clients connected
        assert not starlive.can_push()
        assert not starlive.can_push("user123")

        # Simulate connected clients via internal manager
        starlive._websocket_manager.clients["123"] = ["client1"]
        starlive._websocket_manager.clients["456"] = ["client2"]

        assert starlive.can_push()
        assert starlive.can_push("123")
        assert starlive.can_push("456")
        assert not starlive.can_push("789")

    def test_stream_operations_htmx(self):
        """Test HTMX stream operations."""
        starlive = StarLive()

        # Test all HTMX operations
        operations = {
            "append": ("beforeend", "foo", "#bar"),
            "prepend": ("afterbegin", "foo", "#bar"),
            "replace": ("outerHTML", "foo", "#bar"),
            "update": ("innerHTML", "foo", "#bar"),
            "after": ("afterend", "foo", "#bar"),
            "before": ("beforebegin", "foo", "#bar"),
        }

        for op_name, (action, content, target) in operations.items():
            result = getattr(starlive, op_name)(
                content, target, hypermedia_type=HypermediaType.HTMX
            )
            assert result["type"] == "htmx"
            assert result["action"] == action
            assert result["target"] == target
            assert result["content"] == content

        # Test remove
        remove_result = starlive.remove("#bar", hypermedia_type=HypermediaType.HTMX)
        assert remove_result["type"] == "htmx"
        assert remove_result["action"] == "delete"
        assert remove_result["target"] == "#bar"
        assert remove_result["content"] == ""

    def test_stream_operations_turbo(self):
        """Test Turbo stream operations."""
        starlive = StarLive()

        # Test all Turbo operations
        operations = ["append", "prepend", "replace", "update", "after", "before"]

        for action in operations:
            result = getattr(starlive, action)(
                "foo", "#bar", hypermedia_type=HypermediaType.TURBO
            )
            expected = (
                f'<turbo-stream action="{action}" target="#bar">'
                f"<template>foo</template></turbo-stream>"
            )
            assert result == expected

        # Test remove
        remove_result = starlive.remove("#bar", hypermedia_type=HypermediaType.TURBO)
        expected = (
            '<turbo-stream action="remove" target="#bar">'
            "<template></template></turbo-stream>"
        )
        assert remove_result == expected

    def test_stream_operations_multiple(self):
        """Test stream operations with multiple targets."""
        starlive = StarLive()

        # Test Turbo with multiple targets
        result = starlive.append(
            "foo", ".bars", multiple=True, hypermedia_type=HypermediaType.TURBO
        )
        assert 'targets=".bars"' in result
        assert 'target=".bars"' not in result

        # Test single target (default)
        result = starlive.append("foo", "#bar", hypermedia_type=HypermediaType.TURBO)
        assert 'target="#bar"' in result
        assert 'targets="#bar"' not in result

    def test_stream_response_htmx(self):
        """Test HTMX stream response generation."""
        starlive = StarLive()

        stream = starlive.append("foo", "#bar", hypermedia_type=HypermediaType.HTMX)
        response = starlive.stream(stream, HypermediaType.HTMX)

        assert response.media_type == "text/html"
        assert response.body == b"foo"

    def test_stream_response_turbo(self):
        """Test Turbo stream response generation."""
        starlive = StarLive()

        streams = [
            starlive.append("foo", "#bar", hypermedia_type=HypermediaType.TURBO),
            starlive.remove("#baz", hypermedia_type=HypermediaType.TURBO),
        ]
        response = starlive.stream(streams, HypermediaType.TURBO)

        assert response.media_type == "text/vnd.turbo-stream.html"
        expected = (
            '<turbo-stream action="append" target="#bar">'
            "<template>foo</template></turbo-stream>"
            '<turbo-stream action="remove" target="#baz">'
            "<template></template></turbo-stream>"
        )
        assert response.body.decode() == expected

    def test_user_id_callback(self):
        """Test custom user ID callback."""
        starlive = StarLive()

        @starlive.user_id
        def custom_user_id():
            return "custom_user_123"

        assert starlive.user_id_callback() == "custom_user_123"

    def test_default_user_id(self):
        """Test default user ID generation."""
        starlive = StarLive()

        user_id = starlive._default_user_id()
        assert isinstance(user_id, str)
        assert len(user_id) == 32  # UUID hex string length

    def test_hypermedia_type_constants(self):
        """Test hypermedia type constants."""
        assert HypermediaType.HTMX == "htmx"
        assert HypermediaType.TURBO == "turbo"

    def test_context_processor(self):
        """Test Jinja2 context processor."""
        starlive = StarLive()
        processor = starlive_context_processor(starlive)
        context = processor()

        assert "starlive_scripts" in context
        assert "starlive" in context
        assert context["starlive"] is starlive

    def test_make_stream_internal(self):
        """Test internal stream generation method."""
        starlive = StarLive()

        # Test with single target
        result = starlive._stream_generator._make_turbo_stream(
            "foo", "baz", "bar", False
        )
        expected = '<turbo-stream action="foo" target="bar"><template>baz</template></turbo-stream>'
        assert result == expected

        # Test with multiple targets
        result = starlive._stream_generator._make_turbo_stream(
            "foo", "baz", ".bars", True
        )
        expected = '<turbo-stream action="foo" targets=".bars"><template>baz</template></turbo-stream>'
        assert result == expected

    def test_script_generation_both_types(self):
        """Test script generation for both hypermedia types."""
        starlive = StarLive()

        # Test loading both libraries (default)
        scripts = starlive.get_scripts()
        assert "htmx" in scripts
        assert "turbo" in scripts.lower()
        assert "/starlive-stream" in scripts

    def test_integration_full_request_cycle(self):
        """Test full request cycle with both HTMX and Turbo."""
        app = Starlette()
        starlive = StarLive(app)

        @app.route("/htmx-test", methods=["POST"])
        async def htmx_test(request):
            content = "<div>HTMX Response</div>"
            if request.state.can_stream():
                stream = starlive.update(
                    content, "#target", hypermedia_type=request.state.hypermedia_type
                )
                return starlive.stream(stream, request.state.hypermedia_type)
            return HTMLResponse(content)

        @app.route("/turbo-test", methods=["POST"])
        async def turbo_test(request):
            content = "<div>Turbo Response</div>"
            if request.state.can_stream():
                stream = starlive.update(
                    content, "#target", hypermedia_type=request.state.hypermedia_type
                )
                return starlive.stream(stream, request.state.hypermedia_type)
            return HTMLResponse(content)

        client = TestClient(app)

        # Test HTMX request
        response = client.post("/htmx-test", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert b"HTMX Response" in response.content
        assert response.headers["content-type"] == "text/html; charset=utf-8"

        # Test Turbo request
        response = client.post(
            "/turbo-test", headers={"Accept": "text/vnd.turbo-stream.html"}
        )
        assert response.status_code == 200
        assert b"Turbo Response" in response.content
        assert "text/vnd.turbo-stream.html" in response.headers["content-type"]


def test_push_operations():
    """Test push operations setup and client management."""
    starlive = StarLive()

    # Test that we can add clients to the manager
    starlive._websocket_manager.clients["123"] = ["mock_ws1"]
    starlive._websocket_manager.clients["456"] = ["mock_ws2"]

    # Test that can_push works correctly
    assert starlive.can_push()
    assert starlive.can_push("123")
    assert starlive.can_push("456")
    assert not starlive.can_push("789")

    # Test stream generation for push
    stream = starlive.append("foo", "#bar", hypermedia_type=HypermediaType.HTMX)
    assert stream["type"] == "htmx"
    assert stream["action"] == "beforeend"
    assert stream["target"] == "#bar"
    assert stream["content"] == "foo"


def test_push_to_specific_client():
    """Test push client targeting functionality."""
    starlive = StarLive()

    # Test client management
    starlive._websocket_manager.clients["123"] = ["mock_ws1"]
    starlive._websocket_manager.clients["456"] = ["mock_ws2"]

    # Test specific client targeting
    assert starlive.can_push("456")
    assert not starlive.can_push("nonexistent")

    # Test Turbo stream generation
    stream = starlive.append("foo", "#bar", hypermedia_type=HypermediaType.TURBO)
    expected = '<turbo-stream action="append" target="#bar"><template>foo</template></turbo-stream>'
    assert stream == expected


def test_push_connection_cleanup():
    """Test connection cleanup functionality."""
    starlive = StarLive()

    # Test client management and cleanup
    starlive._websocket_manager.clients["123"] = ["mock_ws_good", "mock_ws_bad"]

    # Test that we can remove clients
    starlive._websocket_manager.clients["123"].remove("mock_ws_bad")
    assert "mock_ws_bad" not in starlive._websocket_manager.clients["123"]
    assert "mock_ws_good" in starlive._websocket_manager.clients["123"]

    # Test stream generation for cleanup scenarios
    stream = starlive.append("foo", "#bar", hypermedia_type=HypermediaType.HTMX)
    assert stream["type"] == "htmx"
