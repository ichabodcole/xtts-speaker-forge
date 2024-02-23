#!/bin/bash

# URLs
CHECKPOINT_URL="https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth"
CONFIG_URL="https://huggingface.co/coqui/XTTS-v2/resolve/main/config.json"
VOCAB_URL="https://huggingface.co/coqui/XTTS-v2/resolve/main/vocab.json"
SPEAKERS_XTTS_URL="https://huggingface.co/coqui/XTTS-v2/resolve/main/speakers_xtts.pth"

# Installation directory
INSTALL_DIR="./model"

# Paths
MODEL_PATH="${INSTALL_DIR}/model.pth"
CONFIG_PATH="${INSTALL_DIR}/config.json"
VOCAB_PATH="${INSTALL_DIR}/vocab.json"
SPEAKERS_XTTS_PATH="${INSTALL_DIR}/speakers_xtts.pth"

# Check if files exist
files_exist() {
  if [[ -f "$MODEL_PATH" && -f "$CONFIG_PATH" && -f "$VOCAB_PATH" && -f "$SPEAKERS_XTTS_PATH" ]]; then
    return 0  # True, in shell script 0 is success/true
  else
    return 1  # False, non-zero is false
  fi
}

# Download files if they do not exist
if ! files_exist; then
  # Ensure the installation directory exists
  mkdir -p "$INSTALL_DIR"

  # Download files
  wget -O "$MODEL_PATH" "$CHECKPOINT_URL"
  wget -O "$CONFIG_PATH" "$CONFIG_URL"
  wget -O "$VOCAB_PATH" "$VOCAB_URL"
  wget -O "$SPEAKERS_XTTS_PATH" "$SPEAKERS_XTTS_URL"
fi

# Set environment variables
export CHECKPOINT_DIR="$INSTALL_DIR"
export CHECKPOINT_PATH="$MODEL_PATH"
export CONFIG_PATH="$CONFIG_PATH"
export VOCAB_PATH="$VOCAB_PATH"
export SPEAKERS_XTTS_PATH="$SPEAKERS_XTTS_PATH"

# Optionally, print or use the environment variables to confirm they're set
echo "CHECKPOINT_DIR=$CHECKPOINT_DIR"
echo "CHECKPOINT_PATH=$CHECKPOINT_PATH"
echo "CONFIG_PATH=$CONFIG_PATH"
echo "VOCAB_PATH=$VOCAB_PATH"
echo "SPEAKERS_XTTS_PATH=$SPEAKERS_XTTS_PATH"

# Note: These environment variables are set for the duration of this script and child processes.
# If you need them in your current shell session, you should source this script instead of executing it.
