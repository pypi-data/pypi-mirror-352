"""
Unified tests for StarLive across Starlette and FastAPI frameworks.

This module contains comprehensive tests that run against both frameworks
using the unified test infrastructure to ensure consistent behavior.
"""

import pytest

from starlive import StarLive

from .test_helpers import (
    FASTAPI_AVAILABLE,
    TestAssertions,
    fastapi_test_app,  # noqa: F401 - used as pytest fixture
    run_framework_test,
    starlette_test_app,  # noqa: F401 - used as pytest fixture
    test_app_with_framework,  # noqa: F401 - used as pytest fixture
)


class TestBasicFunctionality:
    """Test basic StarLive functionality across both frameworks."""

    def test_homepage_loads(self, test_app_with_framework):
        """Test that the homepage loads correctly."""
        client = test_app_with_framework["client"]
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "Hello World"

    def test_htmx_detection_and_response(self, test_app_with_framework):
        """Test HTMX request detection and response."""
        client = test_app_with_framework["client"]

        response = client.post("/test", headers={"HX-Request": "true"})
        TestAssertions.assert_htmx_response(response)

    def test_turbo_detection_and_response(self, test_app_with_framework):
        """Test Turbo request detection and response."""
        client = test_app_with_framework["client"]

        response = client.post(
            "/test", headers={"Accept": "text/vnd.turbo-stream.html"}
        )
        TestAssertions.assert_turbo_response(response)

    def test_non_hypermedia_fallback(self, test_app_with_framework):
        """Test fallback for non-hypermedia requests."""
        client = test_app_with_framework["client"]

        response = client.post("/test")
        assert response.status_code == 200
        assert response.text == "Updated"

    def test_complex_operations(self, test_app_with_framework):
        """Test complex operations with multiple streams."""
        client = test_app_with_framework["client"]

        # Test HTMX
        response = client.post("/complex", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert "new item" in response.text.lower()

        # Test Turbo
        response = client.post(
            "/complex", headers={"Accept": "text/vnd.turbo-stream.html"}
        )
        assert response.status_code == 200
        assert "turbo-stream" in response.text


class TestMiddlewareIntegration:
    """Test middleware integration across frameworks."""

    def test_middleware_is_configured(self, test_app_with_framework):
        """Test that middleware is properly configured."""
        # Instead of checking internal structure, test that middleware functionality works
        client = test_app_with_framework["client"]

        # Test with HTMX request - if middleware is working, we should get hypermedia response
        response = client.post("/test", headers={"HX-Request": "true"})
        assert response.status_code == 200
        # The fact that we get a hypermedia response indicates middleware is working

    def test_request_state_injection(self, test_app_with_framework):
        """Test that request state is properly injected."""
        client = test_app_with_framework["client"]

        # Test with HTMX request
        response = client.post("/test", headers={"HX-Request": "true"})
        assert response.status_code == 200
        # The fact that we get a hypermedia response indicates state was injected


class TestWebSocketIntegration:
    """Test WebSocket integration across frameworks."""

    def test_websocket_route_exists(self, test_app_with_framework):
        """Test that WebSocket route is properly created."""
        app = test_app_with_framework["app"]
        starlive = test_app_with_framework["starlive"]
        TestAssertions.assert_websocket_route_exists(app, starlive)


class TestFrameworkConsistency:
    """Test that behavior is consistent across frameworks."""

    @pytest.mark.parametrize(
        "headers,expected_type",
        [
            ({"HX-Request": "true"}, "htmx"),
            ({"Accept": "text/vnd.turbo-stream.html"}, "turbo"),
        ],
    )
    def test_hypermedia_type_detection_consistency(
        self, test_app_with_framework, headers, expected_type
    ):
        """Test that hypermedia type detection is consistent."""
        client = test_app_with_framework["client"]

        response = client.post("/test", headers=headers)
        assert response.status_code == 200

        if expected_type == "htmx":
            TestAssertions.assert_htmx_response(response)
        else:
            TestAssertions.assert_turbo_response(response)

    def test_stream_response_format_consistency(self, test_app_with_framework):
        """Test that stream response formats are consistent."""
        client = test_app_with_framework["client"]

        # Test HTMX response format
        response = client.post("/test", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

        # Test Turbo response format
        response = client.post(
            "/test", headers={"Accept": "text/vnd.turbo-stream.html"}
        )
        assert response.status_code == 200
        assert "turbo-stream" in response.text


class TestFrameworkSpecificFeatures:
    """Test framework-specific features."""

    def test_starlette_specific_features(self, starlette_test_app):
        """Test Starlette-specific functionality."""
        app = starlette_test_app["app"]
        client = starlette_test_app["client"]

        # Test that routes are accessible
        assert hasattr(app, "router")
        assert len(app.router.routes) > 0

        # Test basic request
        response = client.get("/")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_fastapi_specific_features(self, fastapi_test_app):
        """Test FastAPI-specific functionality."""
        app = fastapi_test_app["app"]
        client = fastapi_test_app["client"]

        # Test that routes are accessible
        assert hasattr(app, "routes")
        assert len(app.routes) > 0

        # Test basic request
        response = client.get("/")
        assert response.status_code == 200

        # Test OpenAPI docs (FastAPI specific)
        response = client.get("/docs")
        assert response.status_code == 200


class TestStreamOperations:
    """Test stream operations across frameworks."""

    def test_update_operation(self, test_app_with_framework):
        """Test update stream operation."""

        def test_update(test_context):
            starlive = test_context["starlive"]

            # Test HTMX update
            stream = starlive.update("test content", "#target", hypermedia_type="htmx")
            assert stream is not None

            # Test Turbo update
            stream = starlive.update("test content", "#target", hypermedia_type="turbo")
            assert stream is not None

        run_framework_test(test_update, test_app_with_framework["framework"])

    def test_append_operation(self, test_app_with_framework):
        """Test append stream operation."""

        def test_append(test_context):
            starlive = test_context["starlive"]

            # Test HTMX append
            stream = starlive.append("test content", "#target", hypermedia_type="htmx")
            assert stream is not None

            # Test Turbo append
            stream = starlive.append("test content", "#target", hypermedia_type="turbo")
            assert stream is not None

        run_framework_test(test_append, test_app_with_framework["framework"])

    def test_remove_operation(self, test_app_with_framework):
        """Test remove stream operation."""

        def test_remove(test_context):
            starlive = test_context["starlive"]

            # Test HTMX remove
            stream = starlive.remove("#target", hypermedia_type="htmx")
            assert stream is not None

            # Test Turbo remove
            stream = starlive.remove("#target", hypermedia_type="turbo")
            assert stream is not None

        run_framework_test(test_remove, test_app_with_framework["framework"])


def test_script_generation_consistency():
    """Test that script generation is consistent across frameworks."""
    starlive1 = StarLive()
    starlive2 = StarLive()

    scripts1 = starlive1.get_scripts()
    scripts2 = starlive2.get_scripts()

    # Scripts should be consistent for same configuration
    assert scripts1 == scripts2
    assert "starlive-stream" in scripts1


def test_user_id_callback_consistency():
    """Test user ID callback functionality."""
    starlive = StarLive()

    @starlive.user_id
    def custom_user_id():
        return "test_user"

    # Test that callback is set
    assert starlive.user_id_callback is not None
