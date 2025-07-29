#!/usr/bin/env python3
"""
FastAPI StarLive Application Example

This example demonstrates how to use StarLive with FastAPI to create
a hypermedia-driven application that automatically detects and supports
both HTMX and Turbo.

This is a simplified version that uses the app factory to reduce code duplication.
"""

import os

import uvicorn

try:
    from examples.app_factory import create_fastapi_app
except ImportError:
    print("Error: FastAPI is not available. Install with: pip install fastapi")
    exit(1)

if __name__ == "__main__":
    print("Starting FastAPI StarLive demo on http://localhost:8002")
    print("Features:")
    print("- HTMX and Turbo Stream support")
    print("- Real-time WebSocket updates")
    print("- Dynamic content management")
    print("- Framework-agnostic hypermedia handling")
    print("- OpenAPI documentation at /docs")
    print()

    try:
        app = create_fastapi_app(debug=True)
        # Disable reload in test environment to avoid uvicorn warnings
        reload = os.getenv("PYTEST_CURRENT_TEST") is None
        uvicorn.run(app, host="0.0.0.0", port=8002, reload=reload)
    except ImportError as e:
        print(f"Error: {e}")
        print("To use FastAPI, install it with: pip install fastapi")
