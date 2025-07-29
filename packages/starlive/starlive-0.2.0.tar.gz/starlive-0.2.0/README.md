# StarLive

> **Universal Hypermedia System for Starlette & FastAPI**
>
> Build dynamic, real-time web applications with automatic HTMX/Turbo detection and WebSocket streaming

[![PyPI version](https://badge.fury.io/py/starlive.svg)](https://pypi.org/project/starlive/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

StarLive automatically detects HTMX/Turbo clients and provides unified streaming responses with real-time WebSocket updates.

## Features

- **Universal API**: One codebase for both HTMX and Turbo
- **Auto-detection**: Framework detection via request headers
- **Real-time**: WebSocket streaming to all clients
- **Zero config**: Works out of the box

## Installation

```bash
pip install starlive
```

## Quick Start

```python
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlive import StarLive, StarLiveMiddleware

starlive = StarLive()

async def homepage(request):
    return HTMLResponse(f"""
    <html>
    <head>{starlive.get_scripts()}</head>
    <body>
        <div id="content">
            <button hx-post="/update" hx-target="#content">Update</button>
        </div>
    </body>
    </html>
    """)

async def update_content(request):
    if request.state.can_stream():
        content = '<div>Updated!</div>'
        if request.state.hypermedia_type == "htmx":
            return HTMLResponse(content)
        else:  # Turbo
            stream = starlive.update(content, "#content",
                                   hypermedia_type=request.state.hypermedia_type)
            return starlive.stream(stream, request.state.hypermedia_type)
    return HTMLResponse("Updated!")

app = Starlette(routes=[
    Route("/", homepage),
    Route("/update", update_content, methods=["POST"]),
])

app.add_middleware(StarLiveMiddleware, starlive=starlive)
app.router.routes.append(starlive.create_websocket_route())
```

## FastAPI

```python
from fastapi import FastAPI, Request
from starlive import StarLive, StarLiveMiddleware

starlive = StarLive()
app = FastAPI()
app.add_middleware(StarLiveMiddleware, starlive=starlive)

@app.websocket(starlive.ws_route)
async def websocket_endpoint(websocket):
    await starlive._websocket_endpoint(websocket)

# Use same handlers as Starlette example
```

## Stream Operations

```python
# All work with both HTMX and Turbo
starlive.append(content, "#target")
starlive.prepend(content, "#target")
starlive.replace(content, "#target")
starlive.update(content, "#target")
starlive.remove("#target")
starlive.before(content, "#target")
starlive.after(content, "#target")
```

## Real-time Updates

```python
# Broadcast to all clients
await starlive.push(
    starlive.append('<div>New message</div>', "#messages"),
    to=None
)

# Custom user identification
@starlive.user_id
def get_user_id():
    return request.session.get("user_id", "anonymous")
```

## Request Detection

```python
if request.state.hypermedia_type == "htmx":
    return HTMLResponse("<div>HTMX response</div>")
elif request.state.hypermedia_type == "turbo":
    return starlive.stream(starlive.update(content, "#target"), "turbo")
else:
    return JSONResponse({"data": "value"})
```

## Templates

```python
from starlette.templating import Jinja2Templates
from starlive import starlive_context_processor

templates = Jinja2Templates(directory="templates")
templates.env.globals.update(starlive_context_processor(starlive)())
```

```html
<head>
  {{ starlive.get_scripts() }}
</head>
```

## Examples

```bash
# Interactive demo
uv run starlive-dev

# Specific frameworks
uv run starlive-dev --framework starlette  # http://localhost:8001
uv run starlive-dev --framework fastapi    # http://localhost:8002
```

## Development

```bash
git clone https://github.com/yourusername/starlive.git
cd starlive
uv sync --dev
```

### Testing

```bash
uv run starlive-test                    # All tests
uv run starlive-test --framework fastapi   # FastAPI only
uv run starlive-test --type e2e             # End-to-end only
uv run starlive-test --coverage             # With coverage
```

### Code Quality

```bash
uv run ruff check src/ tests/ examples/
uv run ruff format src/ tests/ examples/
```

## License

Apache 2.0 License. See [LICENSE](LICENSE) for details.
