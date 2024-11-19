#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (one level up from scripts)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

case "$1" in
    "test")
        if [ -z "$2" ]; then
            # If no second argument, run all tests
            "$PROJECT_ROOT/.venv/bin/python" -m pytest "$PROJECT_ROOT/bot/test" -v --log-cli-level=INFO
        else
            # Run specific test file
            "$PROJECT_ROOT/.venv/bin/python" -m pytest "$PROJECT_ROOT/bot/test/unit/handlers/$2.py" -v --log-cli-level=INFO
        fi
        ;;
    "dev")
        cd "$PROJECT_ROOT/bot" && "$PROJECT_ROOT/.venv/bin/python" core.py
        ;;
    *)
        echo "Unknown command: $1"
        echo "Available commands:"
        echo "  - test [filename.py]  (runs specific test file or all tests if no filename provided)"
        echo "  - dev                 (runs the bot in development mode)"
        exit 1
        ;;
esac 