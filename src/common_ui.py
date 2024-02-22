import gradio as gr
from utils.utils import is_empty_file_list, is_empty_string


def validate_file_uploader(files):
    if is_empty_file_list(files):
        return gr.Button(interactive=False)

    return gr.Button(interactive=True)


def validate_text_box(text):
    if is_empty_string(text):
        return gr.Button(interactive=False)

    return gr.Button(interactive=True)
