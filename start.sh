#!/bin/bash
# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate venv and run
# We redirect stderr to a log file to prevent polluting the stdio channel with logs/banners
# Dive reads from stdout, so stdout must be CLEAN JSON-RPC.
# Logs go to mcp.log
"$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/src/server.py" 2> "$SCRIPT_DIR/mcp.log"
