#!/usr/bin/env python3
"""
Starlette StarLive Application Example

This example demonstrates how to use StarLive with Starlette to create
a hypermedia-driven application that automatically detects and supports
both HTMX and Turbo.

This is a simplified version that uses the app factory to reduce code duplication.
"""

import os

import uvicorn

from examples.app_factory import create_starlette_app

if __name__ == "__main__":
    print("Starting Starlette StarLive demo on http://localhost:8001")
    print("Features:")
    print("- HTMX and Turbo Stream support")
    print("- Real-time WebSocket updates")
    print("- Dynamic content management")
    print("- Framework-agnostic hypermedia handling")
    print()

    app = create_starlette_app(debug=True)
    # Disable reload in test environment to avoid uvicorn warnings
    reload = os.getenv("PYTEST_CURRENT_TEST") is None
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=reload)
