#!/usr/bin/env python3
"""
Basic StarLive Application Example

This example demonstrates how to use StarLive with Starlette to create
a hypermedia-driven application that automatically detects and supports
both HTMX and Turbo.
"""

import time
import uuid
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from starlive import StarLive, starlive_context_processor

# Initialize StarLive
starlive = StarLive()

# Templates - use the correct path whether running from examples/ or project root
template_dir = Path(__file__).parent / "templates"
if not template_dir.exists():
    template_dir = Path("examples/templates")

templates = Jinja2Templates(directory=str(template_dir))
templates.env.globals.update(starlive_context_processor(starlive)())

# Simple in-memory item storage (in production, use a real database)
items_store = {}


async def homepage(request: Request):
    """Homepage that shows both HTMX and Turbo examples."""
    return templates.TemplateResponse(
        "index.html", {"request": request, "items": items_store}
    )


async def add_item(request: Request):
    """Add a new item - works with both HTMX and Turbo."""
    try:
        form = await request.form()
        item_text = form.get("item", "").strip()

        if not item_text:
            return _handle_error(request, "Item cannot be empty")

        # Generate unique ID for the new item
        item_id = str(uuid.uuid4())
        items_store[item_id] = {
            "id": item_id,
            "text": item_text,
            "created_at": time.time(),
        }

        # Create the new item HTML
        item_html = _create_item_html(item_id, item_text)

        # Return appropriate response based on client type
        if request.state.can_stream():
            return _handle_streaming_add(request, item_html)
        else:
            # Fallback for non-hypermedia requests
            return JSONResponse(
                {"success": True, "item_id": item_id, "html": item_html}
            )

    except Exception as e:
        return _handle_error(request, f"Error adding item: {e!s}")


async def delete_item(request: Request):
    """Delete an item - works with both HTMX and Turbo."""
    try:
        item_id = request.path_params["item_id"]

        # Remove from store if exists
        items_store.pop(item_id, None)

        if request.state.can_stream():
            # For hypermedia clients, return appropriate stream
            if request.state.hypermedia_type == "htmx":
                # HTMX expects empty response to remove element
                return HTMLResponse("")
            else:
                # Turbo stream to remove element
                remove_stream = starlive.remove(
                    f"#item-{item_id}", hypermedia_type=request.state.hypermedia_type
                )
                return starlive.stream(remove_stream, request.state.hypermedia_type)
        else:
            return JSONResponse({"success": True, "deleted": item_id})

    except Exception as e:
        return _handle_error(request, f"Error deleting item: {e!s}")


async def push_update(request: Request):
    """Push a real-time update to all connected clients."""
    try:
        timestamp = time.strftime("%H:%M:%S")
        message_html = (
            f'<div class="notification">🔔 Server update at {timestamp}</div>'
        )

        # Push to all clients using HTMX format (will work for both)
        await starlive.push(
            starlive.append(message_html, "#notifications", hypermedia_type="htmx"),
            to=None,  # Send to all clients
        )

        return JSONResponse(
            {"success": True, "message": f"Update sent to all clients at {timestamp}"}
        )

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


async def clear_notifications(request: Request):
    """Clear all notifications."""
    try:
        if request.state.can_stream():
            clear_stream = starlive.update(
                "", "#notifications", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(clear_stream, request.state.hypermedia_type)
        else:
            return JSONResponse({"success": True, "action": "cleared"})

    except Exception as e:
        return _handle_error(request, f"Error clearing notifications: {e!s}")


def _create_item_html(item_id: str, item_text: str) -> str:
    """Create HTML for a new item."""
    return f"""
    <div id="item-{item_id}" class="item">
        <span>{item_text}</span>
        <button type="button"
                hx-delete="/items/{item_id}"
                hx-target="#item-{item_id}"
                hx-swap="delete"
                onclick="if (!this.getAttribute('hx-delete')) fetch('/items/{item_id}/delete', {{method: 'POST'}}).then(() => document.getElementById('item-{item_id}').remove())"
                class="btn btn-danger">
            Delete
        </button>
    </div>
    """


def _handle_error(request: Request, error_message: str) -> HTMLResponse:
    """Handle errors with appropriate response format."""
    if request.state.can_stream():
        if request.state.hypermedia_type == "htmx":
            # For HTMX, return error HTML with 400 status so hx-target-4xx can handle it
            return HTMLResponse(
                f'<div class="error">{error_message}</div>', status_code=400
            )
        else:
            # For Turbo, update error container
            error_stream = starlive.update(
                f'<div class="error">{error_message}</div>',
                "#error-message",
                hypermedia_type=request.state.hypermedia_type,
            )
            return starlive.stream(error_stream, request.state.hypermedia_type)
    else:
        return JSONResponse({"success": False, "error": error_message}, status_code=400)


def _handle_streaming_add(request: Request, item_html: str) -> HTMLResponse:
    """Handle adding item for streaming clients."""
    if request.state.hypermedia_type == "htmx":
        # For HTMX, return the item HTML directly since form targets #items-list
        return HTMLResponse(item_html)
    else:
        # For Turbo, combine streams
        add_item_stream = starlive.append(
            item_html, "#items-list", hypermedia_type=request.state.hypermedia_type
        )
        # Clear error message
        clear_error = starlive.update(
            "", "#error-message", hypermedia_type=request.state.hypermedia_type
        )
        return starlive.stream(
            [add_item_stream, clear_error],
            request.state.hypermedia_type,
        )


# Configure user ID for WebSocket connections
@starlive.user_id
def get_user_id() -> str:
    """In a real app, this would return the current user's ID from session/auth."""
    return str(uuid.uuid4())


# Routes
routes = [
    Route("/", homepage),
    Route("/items", add_item, methods=["POST"]),
    Route("/items/{item_id}", delete_item, methods=["DELETE"]),
    Route(
        "/items/{item_id}/delete", delete_item, methods=["POST"]
    ),  # Fallback for non-DELETE support
    Route("/push", push_update, methods=["POST"]),
    Route("/clear", clear_notifications, methods=["POST"]),
]

# Create the Starlette application
app = Starlette(routes=routes, debug=True)

# Initialize StarLive with the app
starlive.init_app(app)


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting StarLive example app...")
    print("📱 Visit http://localhost:8001 to see the demo")
    print("🔄 The app automatically detects whether you're using HTMX or Turbo!")
    print("📡 WebSocket real-time updates are enabled")

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
