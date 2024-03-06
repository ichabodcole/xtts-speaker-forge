# 1.0.0-alpha.6 (2024-03-05)

## Bug Fixes

- Move speaker metadata to root level property `__speaker_metadata__` to avoid unpacking errors with TTS api lib. Any previously created speaker files will be automatically updated to new format if imported into Speaker Forge on file export.

# 1.0.0-alpha.5 (2024-03-03)

## Bug Fixes

- Import View: unable to read speaker file on cpu device if created on gpu device
- Create View: reset audio player value after file changes

# 1.0.0-alpha.4 (2024-02-29)

## Bug Fixes

- fix tensors running on multiple devices error

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
