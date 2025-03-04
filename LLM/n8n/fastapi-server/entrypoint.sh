#!/bin/sh

if [ "$DEBUG_MODE" = "True" ]; then
    echo "Development mode enabled. Sleeping indefinitely..."
    exec sleep infinity
else
    echo "Production mode enabled. Starting Uvicorn..."
    exec uvicorn app:app --host 0.0.0.0 --port 9999 --reload
fi
