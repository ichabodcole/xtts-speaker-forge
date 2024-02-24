import gradio as gr
from utils.utils import get_random_speech_text


def SpeechPreviewComponent():
    with gr.Group(visible=False) as audio_preview_group:
        # Get a random item from the speech_input_
        input_text = get_random_speech_text()

        audio_player = gr.Audio(
            value=None, format="wav")

        speech_input_textbox = gr.Textbox(
            input_text,
            label="What should I say?",
            placeholder="Type something...",
            lines=3,
            interactive=True
        )

        generate_speech_btn = gr.Button(
            "Generate Speech")

    return audio_preview_group, audio_player, speech_input_textbox, generate_speech_btn
