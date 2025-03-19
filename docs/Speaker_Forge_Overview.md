# Speaker Forge

Speaker Forge is an application that allows users to preview, create, edit, and manipulate TTS-related speaker embeddings. The app is built with a Gradio 5 interface. It can run as a standalone application or in a Google Colab notebook which handles the compute resources, installs dependencies, and launches the interface.

The application loads and manipulates data from a torch .pth file, which contains a dictionary of speaker names and associated gpt_cond_latent/speaker_embedding values. These embeddings can be used to run inference on a TTS model to generate text-to-speech audio output directly within the interface.

Example contents of speaker pth file:

```json
{
  "__speaker_metadata__": {
    "Speaker Name 1": {
      "gender": "male",
      "accent": "american",
      "age": "adult"
    },
    "Speaker Name 2": {
      "gender": "female",
      "accent": "british",
      "age": "young_adult"
    }
  },
  "Speaker Name 1": {
    "gpt_cond_latent": [...],
    "speaker_embedding": [...]
  },
  "Speaker Name 2": {
    "gpt_cond_latent": [...],
    "speaker_embedding": [...]
  }
}
```

## Interface Overview

The application features a tabbed interface with the following views:

### 1. Explore View

- View a list of speaker names embedded in the pth file
- Select a speaker from a dropdown menu
- Enter text and select language for speech generation
- Preview generated speech with the selected speaker's voice
- Audio is output in WAV format for high quality playback

### 2. Create View

- Upload one or more reference WAV files via drag-and-drop or file browser
- Extract embeddings from the uploaded audio files
- Assign weights to each extracted embedding using sliders (range: 1-10)
- Generate a preview of the combined voice
- Save the new voice embedding with a custom name and metadata

### 3. Mix View

- Select multiple existing speakers from the speaker library
- Assign weights to each selected speaker using sliders (range: 1-10)
- Generate a preview of the mixed voice
- Save the mixed voice embedding with a custom name
- Use the "Spicy" randomizer for creative voice combinations

### 4. Edit View

- Rename existing speakers
- Add or modify metadata for speakers (gender, accent, age, etc.)
- Remove speakers from the library
- All changes are saved to a temporary file until exported

### 5. Import View

- Import speakers from external speaker files
- Select which speakers to import
- Merge them with the current speaker library

### 6. Export View

- Select specific speakers to include in the export
- Export selected speakers to a new .pth file
- Download the file to your local system

### 7. About View

- View information about the application
- Access documentation and guides

### 8. Changelog View

- View the version history and latest changes

## Technical Notes

- Built with Gradio 5.22.0 for a responsive, modern interface
- Supports multiple languages for speech generation
- Handles tensor operations efficiently on both CPU and GPU
- Uses WAV format for high-quality audio processing and playback
