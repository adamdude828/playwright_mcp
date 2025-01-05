#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the browser manager in the background
poetry run python -m src.playwright_mcp.browser_manager &
BROWSER_PID=$!

# Wait a moment for the socket to be created
sleep 1

echo "Browser manager started with PID: $BROWSER_PID"
echo "Logs are being written to: logs/browser_manager.log"
echo "You can monitor logs with: tail -f logs/browser_manager.log"
echo
echo "You can now use MCP commands to control browsers"
echo
echo "Example:"
echo "mcp-cli --server playwright call-tool --tool launch-browser --tool-args '{\"browser_type\": \"chromium\", \"headless\": false}'"
echo
echo "To stop the browser manager:"
echo "kill $BROWSER_PID" 