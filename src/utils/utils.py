import os
import random

from constants import speech_input_defaults
# Utils functions


def is_empty_string(x): return x is None or x.strip() == ""


def is_empty_file_list(x): return x is None or len(x) == 0


def is_valid_file(x): return not is_empty_string(x) and os.path.exists(x)


def is_valid_file_list(x): return not is_empty_file_list(
    x) and all([is_valid_file(f) for f in x])


def get_random_speech_text():
    return random.choice(speech_input_defaults)


def format_md_message(message):
    return f"### _{message}_"
