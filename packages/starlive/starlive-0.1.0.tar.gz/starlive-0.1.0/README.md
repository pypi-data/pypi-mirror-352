# StarLive

> Universal Hypermedia System for Starlette & FastAPI

[![PyPI version](https://badge.fury.io/py/starlive.svg)](https://pypi.org/project/starlive/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

StarLive automatically detects and supports both HTMX and Turbo with real-time WebSocket updates. Build dynamic web applications with a unified API.

## Installation

```bash
pip install starlive
```

## Quick Start

```python
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlive import StarLive

app = Starlette()
starlive = StarLive()
starlive.init_app(app)

@app.route("/")
async def homepage(request):
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>StarLive Demo</title>
        {starlive.get_scripts()}
    </head>
    <body>
        <div id="content">
            <button hx-post="/update" hx-target="#content">Update</button>
        </div>
    </body>
    </html>
    """)

@app.route("/update", methods=["POST"])
async def update_content(request):
    if request.state.can_stream():
        content = '<div>Content updated!</div>'
        
        if request.state.hypermedia_type == "htmx":
            return HTMLResponse(content)
        else:  # Turbo
            stream = starlive.update(content, "#content", 
                                   hypermedia_type=request.state.hypermedia_type)
            return starlive.stream(stream, request.state.hypermedia_type)
    
    return HTMLResponse("Updated!")
```

## Real-time Updates

```python
# Push to all clients
await starlive.push(
    starlive.append('<div>New message!</div>', "#messages"),
    to=None
)

# Custom user identification
@starlive.user_id
def get_user_id():
    return request.session.get("user_id", "anonymous")
```

## Stream Operations

```python
# Basic operations work with both HTMX and Turbo
starlive.append(content, "#target")
starlive.prepend(content, "#target") 
starlive.replace(content, "#target")
starlive.update(content, "#target")
starlive.remove("#target")
starlive.before(content, "#target")
starlive.after(content, "#target")
```

## Request Detection

```python
@app.route("/api/data")
async def get_data(request):
    if request.state.hypermedia_type == "htmx":
        return HTMLResponse("<div>HTMX Response</div>")
    elif request.state.hypermedia_type == "turbo":
        stream = starlive.update(content, "#frame", hypermedia_type="turbo")
        return starlive.stream(stream, hypermedia_type="turbo")
    else:
        return JSONResponse({"data": "value"})
```

## Template Integration

```python
from starlette.templating import Jinja2Templates
from starlive import starlive_context_processor

templates = Jinja2Templates(directory="templates")
templates.env.globals.update(starlive_context_processor(starlive)())
```

```html
<!-- In templates -->
<head>
    {{ starlive.get_scripts() }}
</head>
```

## Examples

Run the complete example:

```bash
python examples/basic_app.py
# Visit http://localhost:8001
```

## Development

```bash
git clone https://github.com/yourusername/starlive.git
cd starlive
uv sync --dev
```

```bash
# Tests
uv run pytest tests/ -v

# Formatting
uv run ruff format src/
uv run ruff check src/ --fix
```

## License

Apache 2.0 License. See [LICENSE](LICENSE) for details.

## Credits

- Inspired by [Turbo-Flask](https://github.com/miguelgrinberg/turbo-flask)
