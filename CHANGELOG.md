# 1.0.0-alpha.3 (2024-02-29)

## Features

- Add Import View: ability import speakers from a separate speaker file into the current list of speakers.
- A temp speaker file is now used during app edits to avoid mutating the original speaker file.
- A few additions to the speaker metadata selectable attribute lists
- Code refactoring and file reorganization to improve dev sanity level.

# 1.0.0-alpha.2 (2024-02-28)

## Features

- Add Edit View: ability to rename speakers, add metadata and remove speakers.
- Export View: add ability to select a subset of speakers for file export, does not alter the base speaker file.
- General: speakers are now sorted alphabetically (dropdowns, etc)
- General: add language select for speaker audio generation
- Mix View: improve slider control management and performance

## Bug Fixes

- Mix View: spicy speaker randomizer could result in duplicate speakers

# 1.0.0-alpha.1 (2024-02-26)

## Features

- app: implement mvp ui (yee-haw!)
