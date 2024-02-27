import os
import random
import json

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
