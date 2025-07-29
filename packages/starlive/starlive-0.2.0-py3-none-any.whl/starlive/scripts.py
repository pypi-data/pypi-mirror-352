"""Script generation utilities for hypermedia libraries."""

from typing import List, Optional

from .types import CDNConfig, HypermediaType


class ScriptGenerator:
    """Generates JavaScript and library loading scripts."""

    def __init__(self, ws_route: str = "/starlive-stream"):
        self.ws_route = ws_route

    def get_default_turbo_version(self) -> str:
        """Get the default Turbo version."""
        return CDNConfig.TURBO_VER

    def get_default_htmx_version(self) -> str:
        """Get the default HTMX version."""
        return CDNConfig.HTMX_VER

    def get_scripts(
        self,
        hypermedia_type: Optional[str] = None,
        turbo_version: str = CDNConfig.TURBO_VER,
        htmx_version: str = CDNConfig.HTMX_VER,
        turbo_url: Optional[str] = None,
        htmx_url: Optional[str] = None,
    ) -> str:
        """Generate script tags for the hypermedia library."""
        scripts = []

        if hypermedia_type is None or hypermedia_type == HypermediaType.TURBO:
            scripts.extend(self._get_turbo_scripts(turbo_version, turbo_url))

        if hypermedia_type is None or hypermedia_type == HypermediaType.HTMX:
            scripts.extend(self._get_htmx_scripts(htmx_version, htmx_url))

        return "\n".join(scripts)

    def _get_turbo_scripts(
        self, version: str, custom_url: Optional[str] = None
    ) -> List[str]:
        """Generate Turbo-specific scripts."""
        scripts = []

        if custom_url is None:
            v = f"@{version}" if version else ""
            custom_url = f"{CDNConfig.TURBO_CDN}/npm/{CDNConfig.TURBO_PKG}{v}/dist/turbo.es2017-umd.js"

        scripts.append(f'<script src="{custom_url}"></script>')
        scripts.append(self._get_turbo_websocket_script())

        return scripts

    def _get_htmx_scripts(
        self, version: str, custom_url: Optional[str] = None
    ) -> List[str]:
        """Generate HTMX-specific scripts."""
        scripts = []

        if custom_url is None:
            custom_url = (
                f"{CDNConfig.HTMX_CDN}/{CDNConfig.HTMX_PKG}@{version}/dist/htmx.min.js"
            )

        scripts.append(f'<script src="{custom_url}"></script>')
        scripts.append(self._get_htmx_websocket_script())

        return scripts

    def _get_turbo_websocket_script(self) -> str:
        """Generate Turbo WebSocket connection script."""
        return f"""<script>
            Turbo.connectStreamSource(new WebSocket(`ws${{location.protocol.substring(4)}}//${{location.host}}{self.ws_route}`));
        </script>"""

    def _get_htmx_websocket_script(self) -> str:
        """Generate HTMX WebSocket handling script."""
        return f"""<script>
            // HTMX WebSocket extension for real-time updates
            htmx.onLoad(function() {{
                const ws = new WebSocket(`ws${{location.protocol.substring(4)}}//${{location.host}}{self.ws_route}`);
                ws.onmessage = function(event) {{
                    try {{
                        const data = JSON.parse(event.data);
                        if (data.type === 'htmx') {{
                            htmxApplyUpdate(data);
                        }} else if (data.type === 'htmx_batch') {{
                            data.streams.forEach(stream => htmxApplyUpdate(stream));
                        }}
                    }} catch (error) {{
                        console.error('Error processing WebSocket message:', error);
                    }}
                }};

                ws.onerror = function(error) {{
                    console.error('WebSocket error:', error);
                }};

                function htmxApplyUpdate(data) {{
                    const target = document.querySelector(data.target);
                    if (!target) {{
                        console.warn('Target element not found:', data.target);
                        return;
                    }}

                    switch (data.action) {{
                        case 'innerHTML':
                            target.innerHTML = data.content;
                            break;
                        case 'outerHTML':
                            target.outerHTML = data.content;
                            break;
                        case 'beforebegin':
                            target.insertAdjacentHTML('beforebegin', data.content);
                            break;
                        case 'afterbegin':
                            target.insertAdjacentHTML('afterbegin', data.content);
                            break;
                        case 'beforeend':
                            target.insertAdjacentHTML('beforeend', data.content);
                            break;
                        case 'afterend':
                            target.insertAdjacentHTML('afterend', data.content);
                            break;
                        case 'delete':
                            target.remove();
                            break;
                        default:
                            console.warn('Unknown action:', data.action);
                    }}

                    // Process any new HTMX elements
                    htmx.process(target.parentElement || document.body);
                }}
            }});
        </script>"""
