#!/bin/bash

# Build frontend
echo "Building frontend..."
cd frontend && npm run build && cd ..

echo "Removing old database..."
rm -f test.db

# Start server with debug logging
echo "Starting server with debug logging..."
uvicorn tests.fastapi_agmin.app_test:app_test --reload --log-level debug
