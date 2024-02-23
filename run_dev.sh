#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

cd "$SCRIPT_DIR"

source ./setup.sh
python scripts/dev_watcher.py --file-path src/gradio_app.py --watch-path src