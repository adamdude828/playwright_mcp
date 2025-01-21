#!/bin/bash

# Start MCP server
echo "Starting MCP server..."
mcp-server &
MCP_SERVER_PID=$!

# Wait for server to start
sleep 2

# Start browser daemon
echo "Starting browser daemon..."
mcp-cli --server playwright call-tool --tool start-daemon --tool-args '{}'

# Navigate to example.com in non-headless mode
echo "mcp-cli --server playwright call-tool --tool navigate --tool-args '{\"url\": \"https://example.com\", \"wait_until\": \"networkidle\", \"headless\": false}'"

# Keep script running
echo "Services started. Press Ctrl+C to stop..."
wait $MCP_SERVER_PID 