import gradio as gr
from utils.utils import get_random_speech_text


def SpeechPreviewComponent(content: dict):
    with gr.Group(visible=False) as audio_preview_group:
        # Get a random item from the speech_input_
        input_text = get_random_speech_text()

        audio_player = gr.Audio(
            value=None, format="wav")

        speech_input_textbox = gr.Textbox(
            input_text,
            label=content.get('speech_input_text_label'),
            placeholder=content.get('speech_input_text_placeholder'),
            lines=3,
            interactive=True
        )

        generate_speech_btn = gr.Button(
            content.get('generate_speech_btn_label'))

        generate_speech_btn.click(
            lambda: ([gr.Audio(value=None), gr.Button(interactive=False)]),
            outputs=[
                audio_player,
                generate_speech_btn
            ])

    return audio_preview_group, audio_player, speech_input_textbox, generate_speech_btn
