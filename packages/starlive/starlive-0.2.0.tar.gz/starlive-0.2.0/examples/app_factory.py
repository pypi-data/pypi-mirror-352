#!/usr/bin/env python3
"""
Application factory for creating StarLive examples with different frameworks.

This module provides a unified interface for creating Starlette and FastAPI
applications with the same functionality, reducing code duplication.
"""

import argparse
from typing import Union

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from starlive import StarLive, StarLiveMiddleware, starlive_context_processor

try:
    from fastapi import FastAPI, Form
    from fastapi import Request as FastAPIRequest
    from fastapi.responses import HTMLResponse as FastAPIHTMLResponse
    from fastapi.templating import Jinja2Templates as FastAPIJinja2Templates

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from examples.shared import (
    add_item_logic,
    clear_notifications_logic,
    delete_item_logic,
    get_template_dir,
    get_user_id,
    items_store,
    push_update_logic,
)


def create_starlette_app(debug: bool = True, port: int = 8001) -> Starlette:
    """Create a Starlette application with StarLive."""

    # Initialize StarLive
    starlive = StarLive()

    # Set up templates
    templates = Jinja2Templates(directory=str(get_template_dir()))
    templates.env.globals.update(starlive_context_processor(starlive)())

    async def homepage(request: Request):
        """Homepage that shows both HTMX and Turbo examples."""
        return templates.TemplateResponse(
            "index.html", {"request": request, "items": items_store}
        )

    async def add_item(request: Request):
        """Add a new item - works with both HTMX and Turbo."""
        form = await request.form()
        item_text = form.get("item", "")
        return await add_item_logic(request, item_text, starlive)

    async def delete_item(request: Request):
        """Delete an item - works with both HTMX and Turbo."""
        item_id = request.path_params["item_id"]
        return await delete_item_logic(request, item_id, starlive)

    async def push_update(request: Request):
        """Push a real-time update to all connected clients."""
        return await push_update_logic(starlive)

    async def clear_notifications(request: Request):
        """Clear all notifications."""
        return await clear_notifications_logic(request, starlive)

    # Create routes
    routes = [
        Route("/", homepage),
        Route("/items", add_item, methods=["POST"]),
        Route("/items/{item_id}", delete_item, methods=["DELETE"]),
        Route("/items/{item_id}/delete", delete_item, methods=["POST"]),  # Fallback
        Route("/push", push_update, methods=["POST"]),
        Route("/clear", clear_notifications, methods=["POST"]),
    ]

    # Create application
    app = Starlette(debug=debug, routes=routes)

    # Add StarLive middleware and WebSocket route
    app.add_middleware(StarLiveMiddleware, starlive=starlive)
    app.router.routes.append(starlive.create_websocket_route())

    # Set up user ID callback
    @starlive.user_id
    def user_id_callback():
        return get_user_id()

    return app


def create_fastapi_app(debug: bool = True, port: int = 8002) -> "FastAPI":
    """Create a FastAPI application with StarLive."""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is not available. Install with: pip install fastapi")

    # Initialize StarLive
    starlive = StarLive()

    # Set up templates
    templates = FastAPIJinja2Templates(directory=str(get_template_dir()))
    templates.env.globals.update(starlive_context_processor(starlive)())

    # Create the FastAPI application
    app = FastAPI(title="StarLive FastAPI Demo", debug=debug)

    # Add StarLive middleware
    app.add_middleware(StarLiveMiddleware, starlive=starlive)

    # Add WebSocket route for StarLive
    @app.websocket(starlive.ws_route)
    async def websocket_endpoint(websocket):
        await starlive._websocket_endpoint(websocket)

    @app.get("/", response_class=FastAPIHTMLResponse)
    async def homepage(request: FastAPIRequest):
        """Homepage that shows both HTMX and Turbo examples."""
        return templates.TemplateResponse(
            "index.html", {"request": request, "items": items_store}
        )

    @app.post("/items")
    async def add_item(request: FastAPIRequest, item: str = Form(...)):
        """Add a new item - works with both HTMX and Turbo."""
        return await add_item_logic(request, item, starlive)

    @app.delete("/items/{item_id}")
    @app.post("/items/{item_id}/delete")  # Fallback for non-DELETE support
    async def delete_item(request: FastAPIRequest, item_id: str):
        """Delete an item - works with both HTMX and Turbo."""
        return await delete_item_logic(request, item_id, starlive)

    @app.post("/push")
    async def push_update(request: FastAPIRequest):
        """Push a real-time update to all connected clients."""
        return await push_update_logic(starlive)

    @app.post("/clear")
    async def clear_notifications(request: FastAPIRequest):
        """Clear all notifications."""
        return await clear_notifications_logic(request, starlive)

    # Set up user ID callback
    @starlive.user_id
    def user_id_callback():
        return get_user_id()

    return app


def create_app(framework: str = "starlette", **kwargs) -> Union[Starlette, "FastAPI"]:
    """Create an application using the specified framework.

    Args:
        framework: Either "starlette" or "fastapi"
        **kwargs: Additional arguments passed to the app factory

    Returns:
        The created application instance

    Raises:
        ValueError: If framework is not supported
        ImportError: If FastAPI is requested but not available
    """
    if framework.lower() == "starlette":
        return create_starlette_app(**kwargs)
    elif framework.lower() == "fastapi":
        return create_fastapi_app(**kwargs)
    else:
        raise ValueError(
            f"Unsupported framework: {framework}. Use 'starlette' or 'fastapi'"
        )


def main():
    """Main entry point for the application factory script."""

    import uvicorn

    parser = argparse.ArgumentParser(description="Run StarLive demo application")
    parser.add_argument(
        "--framework",
        "-f",
        choices=["starlette", "fastapi"],
        default="starlette",
        help="Framework to use (default: starlette)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=None,
        help="Port to run on (default: 8001 for Starlette, 8002 for FastAPI)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Set default ports
    if args.port is None:
        args.port = 8001 if args.framework == "starlette" else 8002

    print(f"Starting {args.framework.title()} application on port {args.port}")

    try:
        app = create_app(args.framework, debug=args.debug, port=args.port)
        uvicorn.run(app, host="0.0.0.0", port=args.port, reload=args.debug)
    except ImportError as e:
        print(f"Error: {e}")
        print("To use FastAPI, install it with: uv add fastapi")
        return 1
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Run StarLive demo application")
    parser.add_argument(
        "--framework",
        "-f",
        choices=["starlette", "fastapi"],
        default="starlette",
        help="Framework to use (default: starlette)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=None,
        help="Port to run on (default: 8001 for Starlette, 8002 for FastAPI)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Set default ports
    if args.port is None:
        args.port = 8001 if args.framework == "starlette" else 8002

    print(f"Starting {args.framework.title()} application on port {args.port}")

    try:
        app = create_app(args.framework, debug=args.debug, port=args.port)
        uvicorn.run(app, host="0.0.0.0", port=args.port, reload=args.debug)
    except ImportError as e:
        print(f"Error: {e}")
        print("To use FastAPI, install it with: uv add fastapi")
    except Exception as e:
        print(f"Error starting application: {e}")
