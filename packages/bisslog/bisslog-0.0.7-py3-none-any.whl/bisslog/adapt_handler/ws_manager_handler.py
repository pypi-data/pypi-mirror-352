"""This module defines the web socket manager handler, an adapter handler
responsible for managing web socket operations."""
from .adapt_handler import AdaptHandler


class WSManagerHandler(AdaptHandler):
    """Handler for managing web socket operations

    This class serves as an adapter handler for message emitting, allowing
    the integration of different websocket systems.

    It extends `AdaptHandler` to provide a structured way to handle
    web socket manager dynamically."""


bisslog_ws = WSManagerHandler("websocket-manager-default")
