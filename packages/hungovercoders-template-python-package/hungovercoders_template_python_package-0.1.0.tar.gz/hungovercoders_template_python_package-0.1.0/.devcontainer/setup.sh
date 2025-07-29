#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "Installing development requirements..."
python -m pip install -r .devcontainer/requirements_dev.txt

echo "Installing documentation requirements..."
python -m pip install -r .devcontainer/requirements_docs.txt

echo "Setup complete!"
