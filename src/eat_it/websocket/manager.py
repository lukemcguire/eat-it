"""WebSocket connection manager for shopping list real-time sync."""

import logging
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ListConnectionManager:
    """Manages WebSocket connections per shopping list.

    Each shopping list has its own "room" of connected clients.
    Changes to a list are broadcast only to clients viewing that list.
    """

    def __init__(self):
        # Map: list_id -> set of websocket connections
        self.connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, list_id: int, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection for a list."""
        await websocket.accept()
        if list_id not in self.connections:
            self.connections[list_id] = set()
        self.connections[list_id].add(websocket)
        logger.debug(
            "WebSocket connected to list %s. Total connections: %s",
            list_id,
            len(self.connections[list_id])
        )

    def disconnect(self, list_id: int, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from a list room."""
        if list_id in self.connections:
            self.connections[list_id].discard(websocket)
            if not self.connections[list_id]:
                del self.connections[list_id]
            logger.debug(
                "WebSocket disconnected from list %s", list_id
            )

    async def broadcast_to_list(
        self,
        list_id: int,
        message: dict,
        exclude: WebSocket | None = None
    ) -> None:
        """Send a message to all clients viewing a specific list.

        Args:
            list_id: The shopping list ID
            message: Dict to send as JSON
            exclude: Optional WebSocket to exclude (sender)
        """
        if list_id not in self.connections:
            return

        dead_connections = set()
        for connection in self.connections[list_id]:
            if connection == exclude:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)

        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(list_id, dead)

    def get_connection_count(self, list_id: int) -> int:
        """Return number of active connections for a list."""
        return len(self.connections.get(list_id, set()))


# Global manager instance
manager = ListConnectionManager()
