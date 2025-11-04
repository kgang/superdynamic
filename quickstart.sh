#!/bin/bash

# MCP OAuth DCR - Quick Start Script
# This script starts the server and runs a client demo

set -e  # Exit on error

echo "========================================================================"
echo "MCP OAuth DCR - Quick Start"
echo "========================================================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.10+ is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detected"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
pip install -q -r server/requirements.txt

# Start server in background
echo ""
echo "🚀 Starting MCP Server..."
cd server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../server.log 2>&1 &
SERVER_PID=$!
cd ..

echo "   Server PID: $SERVER_PID"
echo "   Server URL: http://localhost:8000"

# Wait for server to be ready
echo ""
echo "⏳ Waiting for server to start..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Server is ready!"
        break
    fi

    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Server failed to start within 60 seconds"
        echo "Check server.log for details"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi

    sleep 2
done

echo ""
echo "========================================================================"
echo "Choose an option:"
echo "========================================================================"
echo "  1) Run automated client test (no browser, headless)"
echo "  2) Run interactive client demo (opens browser for OAuth)"
echo "  3) Just leave server running"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🧪 Running automated client test..."
        python test_client.py
        echo ""
        echo "✅ Test completed successfully!"
        ;;
    2)
        echo ""
        echo "🎯 Running interactive client demo..."
        echo "   (This will open your browser for OAuth authorization)"
        echo ""
        sleep 2
        python client.py --server-url http://localhost:8000 --demo
        ;;
    3)
        echo ""
        echo "✓ Server is running at http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        echo ""
        echo "Press Ctrl+C to stop"
        wait $SERVER_PID
        exit 0
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

# Cleanup
echo ""
read -p "Stop server? (y/n): " stop
if [ "$stop" = "y" ]; then
    echo "🛑 Stopping server..."
    kill $SERVER_PID 2>/dev/null || true
    sleep 2
    kill -9 $SERVER_PID 2>/dev/null || true
    echo "✓ Server stopped"
else
    echo "Server still running (PID: $SERVER_PID)"
    echo "To stop: kill $SERVER_PID"
fi

echo ""
echo "========================================================================"
echo "Quick Start Complete!"
echo "========================================================================"
