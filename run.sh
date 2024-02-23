#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

cd "$SCRIPT_DIR"

source ./setup.sh
python src/gradio_app.py
