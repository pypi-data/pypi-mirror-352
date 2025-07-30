@echo off
REM Run script for Laban Movement Analysis MCP Server (Windows)

echo 🎭 Starting Laban Movement Analysis MCP Server...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Install dependencies if needed
echo Checking dependencies...
pip install -q -r backend\requirements-mcp.txt

REM Set Python path
set PYTHONPATH=%PYTHONPATH%;%cd%

REM Run MCP server
echo.
echo Starting MCP server...
echo Use Ctrl+C to stop the server
echo.
python -m backend.mcp_server 