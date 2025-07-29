"""
Abstract WebSocket manager interface for adaptable implementations.

This module defines a contract (port) for WebSocket communication
in the `bisslog` architecture. It is designed to support multiple backends
such as Flask-SocketIO, AWS Lambda WebSocket API, FastAPI WebSocket, and others.

Implementations of this interface should encapsulate the low-level WebSocket
communication details, allowing the domain layer to remain infrastructure-agnostic.
"""

from abc import ABC, abstractmethod
from typing import Any


class WebSocketManager(ABC):
    """
    Abstract interface for WebSocket communication management.

    This class defines a contract for sending messages, managing rooms,
    and handling connections across different WebSocket backends.

    Implementations of this interface may adapt WebSocket engines like:
    - Flask-SocketIO
    - AWS API Gateway WebSocket (via Lambda)
    - FastAPI WebSocket endpoints
    - Custom socket layers

    Parameters
    ----------
    conn : Any
        A low-level connection or engine instance (e.g., SocketIO, AWS event context).
    """

    def __init__(self, conn: Any) -> None:
        """
        Initialize the WebSocket manager with a backend connection object.

        Parameters
        ----------
        conn : Any
            The backend connection or context to be used by the manager.
        """
        self.conn = conn

    @abstractmethod
    def emit(self, event: str, connection_id: str, payload: Any,
             broadcast: bool = False, to: str = None):
        """
        Emit a message to a specific connection or broadcast to a group.

        Parameters
        ----------
        event : str
            The event name to emit (e.g., "message").
        connection_id : str
            Unique identifier for the connection (e.g., SID or AWS connection ID).
        payload : Any
            The message content to send.
        broadcast : bool, optional
            Whether to send the message to all clients in the room (default is False).
        to : str, optional
            A room or target connection group to broadcast to.

        Raises
        ------
        NotImplementedError
            Must be implemented in subclass.
        """
        raise NotImplementedError("Method 'emit' must be implemented")  # pragma: no cover

    @abstractmethod
    def join_room(self, room: str, connection_id: str):
        """
        Add a connection to a room or group.

        Parameters
        ----------
        room : str
            The name of the room.
        connection_id : str
            The identifier of the connection to add.

        Raises
        ------
        NotImplementedError
            Must be implemented in subclass.
        """
        raise NotImplementedError("Method 'join_room' must be implemented")  # pragma: no cover

    @abstractmethod
    def leave_room(self, room: str, connection_id: str):
        """
        Remove a connection from a room or group.

        Parameters
        ----------
        room : str
            The name of the room.
        connection_id : str
            The identifier of the connection to remove.

        Raises
        ------
        NotImplementedError
            Must be implemented in subclass.
        """
        raise NotImplementedError("Method 'leave_room' must be implemented")  # pragma: no cover

    @abstractmethod
    def rooms(self, connection_id: str):
        """
        List all rooms that a connection is currently part of.

        Parameters
        ----------
        connection_id : str
            The identifier of the connection.

        Returns
        -------
        list[str]
            A list of room names the connection is part of.

        Raises
        ------
        NotImplementedError
            Must be implemented in subclass.
        """
        raise NotImplementedError("Method 'rooms' must be implemented")  # pragma: no cover

    @abstractmethod
    def send(self, event: str, payload: Any = None, connection_id: str = None):
        """
        Send a message without explicitly emitting an event.

        This is useful for simpler payloads or engine-specific semantics.

        Parameters
        ----------
        event : str
            A message type or name.
        payload : Any, optional
            The message content.
        connection_id : str, optional
            The connection to send the message to. May be omitted for broadcast.

        Raises
        ------
        NotImplementedError
            Must be implemented in subclass.
        """
        raise NotImplementedError("Method 'send' must be implemented")  # pragma: no cover
