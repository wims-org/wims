import threading
from fastapi import WebSocket

import logging

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)


# Todo: Change to manage EventSource connections
class WebSocketManager:
    def __init__(self):
        self.connections = {}
        self.lock = threading.Lock()

    async def send_message(self, message, param):
        with self.lock:
            logger.debug(self.connections)
            if param in self.connections:
                for connection in self.connections[param]:
                    try:
                        await connection.send_text(message)
                    except Exception as e:
                        logger.debug(f"Error sending message to WebSocket: {e}")

    async def connect(self, websocket: WebSocket, param):
        await websocket.accept()
        with self.lock:
            if param not in self.connections:
                self.connections[param] = []
            self.connections[param].append(websocket)
        logger.debug(self.connections, param)
        try:
            while True:
                await websocket.receive_text()
        except Exception as e:
            logger.debug(f"WebSocket connection error: {e}")
        finally:
            with self.lock:
                self.connections[param].remove(websocket)
                if not self.connections[param]:
                    del self.connections[param]

    async def broadcast(self, message):
        with self.lock:
            for param, connections in self.connections.items():
                for connection in connections:
                    try:
                        await connection.send_text(message)
                    except Exception as e:
                        logger.debug(f"Error broadcasting message to WebSocket: {e}")
