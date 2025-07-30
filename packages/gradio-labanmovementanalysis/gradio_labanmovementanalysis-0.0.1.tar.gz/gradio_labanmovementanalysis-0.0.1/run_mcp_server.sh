#!/bin/bash

# Run script for Laban Movement Analysis MCP Server

echo "🎭 Starting Laban Movement Analysis MCP Server..."
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install dependencies if needed
echo "Checking dependencies..."
pip install -q -r backend/requirements-mcp.txt

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run MCP server
echo ""
echo "Starting MCP server..."
echo "Use Ctrl+C to stop the server"
echo ""
python -m backend.mcp_server 