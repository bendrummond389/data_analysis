#!/bin/bash

# Clean Python cache files
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Clean build artifacts
rm -rf build/ dist/ *.egg-info/

# Clean log files
find . -type f -name "*.log" -delete

# Clean IDE files
find . -type f -name ".DS_Store" -delete
find . -type f -name "Thumbs.db" -delete

echo "Project cleaned successfully"