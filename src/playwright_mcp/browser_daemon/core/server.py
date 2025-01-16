import asyncio
import json
import os
import tempfile
from asyncio import StreamReader, StreamWriter
from typing import Callable, Dict, Any

from .logging import setup_logging

logger = setup_logging("server")


class UnixSocketServer:
    def __init__(self):
        self._socket_path = os.path.join(tempfile.gettempdir(), 'playwright_mcp.sock')

    async def start(self, connection_handler: Callable):
        """Start the Unix socket server."""
        # Remove existing socket if it exists
        try:
            os.unlink(self._socket_path)
        except OSError:
            if os.path.exists(self._socket_path):
                raise

        server = await asyncio.start_unix_server(
            connection_handler,
            self._socket_path
        )

        logger.info(f"Server listening on {self._socket_path}")
        async with server:
            await server.serve_forever()

    @staticmethod
    async def read_command(reader: StreamReader) -> Dict[str, Any]:
        """Read and parse a command from the client."""
        try:
            data = await reader.readline()
            if not data:
                return {}
            return json.loads(data.decode())
        except Exception as e:
            logger.error(f"Error reading command: {e}")
            return {}

    @staticmethod
    async def send_response(writer: StreamWriter, response: Dict[str, Any]):
        """Send a response back to the client."""
        try:
            response_json = json.dumps(response, ensure_ascii=False)
            writer.write(response_json.encode() + b"\n")
            await writer.drain()
        except Exception as e:
            logger.error(f"Error sending response: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    def cleanup(self):
        """Clean up the socket file."""
        if os.path.exists(self._socket_path):
            os.unlink(self._socket_path) 