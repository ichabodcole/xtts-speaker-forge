import os
import random
import json
import re


from constants.ui_text import speech_input_defaults
# Utils functions


def is_empty_string(x): return x is None or x.strip() == ""


def is_empty_file_list(x): return x is None or len(x) == 0


def is_valid_file(x): return not is_empty_string(x) and os.path.exists(x)


def is_valid_file_list(x): return not is_empty_file_list(
    x) and all([is_valid_file(f) for f in x])


def get_random_speech_text():
    return random.choice(speech_input_defaults)


def format_notification(message: str):
    return f"### _{message}_"


def find_in_tuple_list(item, tuple_list):
    for tuple_item in tuple_list:
        if item in tuple_item:
            return tuple_item

    return None


def get_cur_file_dir():
    return os.path.dirname(os.path.realpath(__file__))


def load_changelog_md():
    script_dir = get_cur_file_dir()
    change_log_location = os.path.join(script_dir, "../../CHANGELOG.md")

    if os.path.exists(change_log_location):
        with open(change_log_location, "r") as f:
            return f.read()


def get_latest_changelog_version():
    changelog = load_changelog_md()

    if changelog:
        # find first line that starts with #
        for line in changelog.split("\n"):
            if line.startswith("# "):
                return line.split(" ")[1]
    else:
        return "NA"


def load_readme_md():
    script_dir = get_cur_file_dir()
    about_location = os.path.join(script_dir, "../../README.md")

    if os.path.exists(about_location):
        with open(about_location, "r") as f:
            return f.read()

def audio_to_compressed_bytes(audio_path: str) -> bytes:
    """Convert an audio file to compressed MP3 bytes"""
    from pydub import AudioSegment
    import io
    
    # Load audio file
    audio = AudioSegment.from_file(audio_path)
    
    # Convert to MP3 with reasonable quality (128kbps)
    buffer = io.BytesIO()
    audio.export(buffer, format="mp3", bitrate="128k")
    buffer.seek(0)
    
    return buffer.read()


def compressed_bytes_to_audio_file(audio_bytes: bytes) -> str:
    """Convert compressed audio bytes to a temporary WAV file and return the path"""
    import tempfile
    from pydub import AudioSegment
    import io
    
    # Create a temporary file for the extracted audio
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        # Convert MP3 bytes back to WAV
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        audio.export(temp_file.name, format="wav")
        return temp_file.name
