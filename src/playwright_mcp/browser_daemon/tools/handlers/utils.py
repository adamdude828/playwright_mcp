import asyncio
import json
import os
import logging
import traceback


# Configure logging
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# File handler
handler = logging.handlers.RotatingFileHandler(
    "logs/mcp_server.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def send_to_manager(command: str, args: dict) -> dict:
    """Send a command to the browser manager service."""
    default_tmp = '/var/folders/h4/mjtjzn8s3d70dkt5y8ym2mp00000gn/T'
    socket_path = os.path.join(os.getenv('TMPDIR', default_tmp), 'playwright_mcp.sock')
    logger.info(f"Connecting to browser manager at {socket_path}")

    try:
        reader, writer = await asyncio.open_unix_connection(socket_path)
        logger.debug("Connected to browser manager")

        # Send request
        request = {"command": command, "args": args}
        logger.debug(f"Sending request: {request}")
        writer.write(json.dumps(request).encode() + b'\n')
        await writer.drain()

        # Get response
        logger.debug("Waiting for response...")
        response = await reader.readline()
        response_data = json.loads(response.decode())
        logger.debug(f"Received response: {response_data}")

        writer.close()
        await writer.wait_closed()
        return response_data
    except Exception as e:
        logger.error(f"Error communicating with browser manager: {e}")
        logger.error(traceback.format_exc())
        raise
