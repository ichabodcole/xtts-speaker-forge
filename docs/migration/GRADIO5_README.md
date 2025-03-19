# Speaker Forge - Gradio 5 Migration

This document provides instructions for testing and completing the Gradio 5 migration.

## Overview

We are migrating Speaker Forge from Gradio 4.19.2 to Gradio 5.22.0. This migration includes:
- Updating all components for Gradio 5 compatibility
- Setting explicit audio format parameters
- Testing and updating tab functionality
- Ensuring event handling works properly

## How to Test

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Individual Components

The following test scripts have been created to verify Gradio 5 compatibility:

```bash
# Test basic components
python src/test_components.py

# Test the setup view
python src/test_setup_view.py

# Test a minimal version of the app
python src/gradio5_test.py
```

### 3. Run with Environment Variables

When running the full application, you need to set the required environment variables:

```bash
CHECKPOINT_DIR=/path/to/checkpoint \
CONFIG_PATH=/path/to/config.json \
VOCAB_PATH=/path/to/vocab.json \
SPEAKERS_XTTS_PATH=/path/to/speakers.pth \
python src/gradio_app.py
```

## Key Changes Made

1. **Audio Format Handling**
   - Set explicit `format="wav"` in Audio components
   - Previously Gradio 4 would convert to WAV automatically, Gradio 5 does not

2. **Tab Handling**
   - Updated tab interface for Gradio 5 compatibility
   - Ensured tab interactivity controls work as expected

3. **Server-Side Rendering (SSR)**
   - Disabled SSR with `ssr_mode=False` to avoid potential issues
   - SSR can be enabled once the migration is stable

## Migration Progress

See `GRADIO5_MIGRATION.md` for detailed progress tracking.

## Known Issues

- None reported yet. Please add any issues encountered here.

## Next Steps

1. Complete the migration of all views
2. Test with real data
3. Add more thorough test cases
4. Test with SSR enabled

## Rollback Plan

If critical issues are encountered, you can switch back to Gradio 4.19.2 by:

1. Updating requirements.txt to specify `gradio==4.19.2`
2. Reverting any component changes that are incompatible 