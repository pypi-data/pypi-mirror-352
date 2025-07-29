#!/usr/bin/env python3
"""
Shared business logic and utilities for StarLive examples.

This module contains framework-agnostic functions that work with both
Starlette and FastAPI, reducing code duplication.
"""

import time
import uuid
from pathlib import Path
from typing import Any, Dict, Union

from starlette.responses import HTMLResponse, JSONResponse

from starlive import StarLive

# Simple in-memory item storage (in production, use a real database)
items_store: Dict[str, Dict[str, Any]] = {}


def get_template_dir() -> Path:
    """Get the templates directory path, handling both development and package scenarios."""
    template_dir = Path(__file__).parent / "templates"
    if not template_dir.exists():
        template_dir = Path("examples/templates")
    return template_dir


def create_item_html(item_id: str, item_text: str) -> str:
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


def handle_error(
    request, error_message: str, starlive: StarLive
) -> Union[HTMLResponse, JSONResponse]:
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


def handle_streaming_add(
    request, item_html: str, starlive: StarLive
) -> Union[HTMLResponse, JSONResponse]:
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


async def add_item_logic(
    request, item_text: str, starlive: StarLive
) -> Union[HTMLResponse, JSONResponse]:
    """Common logic for adding items."""
    try:
        item_text = item_text.strip()

        if not item_text:
            return handle_error(request, "Item cannot be empty", starlive)

        # Generate unique ID for the new item
        item_id = str(uuid.uuid4())
        items_store[item_id] = {
            "id": item_id,
            "text": item_text,
            "created_at": time.time(),
        }

        # Create the new item HTML
        item_html = create_item_html(item_id, item_text)

        # Return appropriate response based on client type
        if request.state.can_stream():
            return handle_streaming_add(request, item_html, starlive)
        else:
            # Fallback for non-hypermedia requests
            return JSONResponse(
                {"success": True, "item_id": item_id, "html": item_html}
            )

    except Exception as e:
        return handle_error(request, f"Error adding item: {e!s}", starlive)


async def delete_item_logic(
    request, item_id: str, starlive: StarLive
) -> Union[HTMLResponse, JSONResponse]:
    """Common logic for deleting items."""
    try:
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
        return handle_error(request, f"Error deleting item: {e!s}", starlive)


async def push_update_logic(starlive: StarLive) -> JSONResponse:
    """Common logic for pushing updates."""
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


async def clear_notifications_logic(
    request, starlive: StarLive
) -> Union[HTMLResponse, JSONResponse]:
    """Common logic for clearing notifications."""
    try:
        if request.state.can_stream():
            clear_stream = starlive.update(
                "", "#notifications", hypermedia_type=request.state.hypermedia_type
            )
            return starlive.stream(clear_stream, request.state.hypermedia_type)
        else:
            return JSONResponse({"success": True, "action": "cleared"})

    except Exception as e:
        return handle_error(request, f"Error clearing notifications: {e!s}", starlive)


def get_user_id() -> str:
    """Get user ID for WebSocket connections."""
    return "demo_user"
