#!/bin/bash

# Generate directory structure excluding model and screenshots directories
# and save it to docs/directory_structure.md
python scripts/generate_directory_tree.py -x model screenshots -o docs/directory_structure.md

echo "Directory structure has been generated in docs/directory_structure.md" 