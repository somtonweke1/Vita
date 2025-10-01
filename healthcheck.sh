#!/bin/bash
# Simple health check for Koyeb
curl -f http://localhost:${PORT:-8000}/health || exit 1
