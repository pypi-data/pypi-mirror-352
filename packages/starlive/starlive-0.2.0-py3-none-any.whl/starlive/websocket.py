"""WebSocket connection management for StarLive."""

import json
import logging
from typing import Callable, List, Optional, Union

from starlette.websockets import WebSocket, WebSocketDisconnect

from .types import ClientRegistry, StreamContent, UserIdType

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self, user_id_callback: Callable[[], str]):
        self.clients: ClientRegistry = {}
        self.user_id_callback = user_id_callback

    async def connect(self, websocket: WebSocket) -> Optional[str]:
        """Accept a new WebSocket connection and register the client."""
        await websocket.accept()
        user_id = self.user_id_callback()

        if user_id not in self.clients:
            self.clients[user_id] = []
        self.clients[user_id].append(websocket)

        logger.info(f"WebSocket connected for user {user_id}")
        return user_id

    async def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Disconnect a WebSocket and clean up client registry."""
        try:
            if user_id in self.clients:
                self.clients[user_id].remove(websocket)
                if not self.clients[user_id]:
                    del self.clients[user_id]
            logger.info(f"WebSocket disconnected for user {user_id}")
        except ValueError:
            # WebSocket was already removed
            pass

    async def handle_connection(self, websocket: WebSocket) -> None:
        """Handle a WebSocket connection lifecycle."""
        user_id = await self.connect(websocket)
        if user_id is None:
            return

        try:
            while True:
                # Keep connection alive by receiving ping/pong or other messages
                message = await websocket.receive_text()
                # Handle any client-side messages here if needed
                logger.debug(f"Received message from {user_id}: {message}")
        except WebSocketDisconnect:
            await self.disconnect(websocket, user_id)
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
            await self.disconnect(websocket, user_id)

    def can_push(self, to: UserIdType = None) -> bool:
        """Check if push notifications can be sent."""
        if to is None:
            return len(self.clients) > 0
        return to in self.clients

    async def push(
        self, stream: StreamContent, to: Optional[Union[str, List[str]]] = None
    ) -> None:
        """Push a stream update to one or more clients."""
        if to is None:
            to = list(self.clients.keys())
        elif isinstance(to, str):
            to = [to]

        message = self._prepare_message(stream)

        for recipient in to:
            if recipient in self.clients:
                await self._send_to_client(recipient, message)

    def _prepare_message(self, stream: StreamContent) -> str:
        """Prepare message content for WebSocket transmission."""
        if isinstance(stream, dict):
            return json.dumps(stream)
        elif isinstance(stream, list):
            if all(isinstance(s, dict) for s in stream):
                # HTMX format - multiple operations
                return json.dumps({"type": "htmx_batch", "streams": stream})
            else:
                # Turbo format - concatenated streams
                return "".join(str(s) for s in stream)
        else:
            return str(stream)

    async def _send_to_client(self, user_id: str, message: str) -> None:
        """Send message to all WebSocket connections for a user."""
        if user_id not in self.clients:
            return

        # Copy list to avoid modification during iteration
        connections = self.clients[user_id][:]

        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send message to {user_id}: {e}")
                # Remove disconnected client
                try:
                    self.clients[user_id].remove(ws)
                    if not self.clients[user_id]:
                        del self.clients[user_id]
                except (ValueError, KeyError):
                    pass
