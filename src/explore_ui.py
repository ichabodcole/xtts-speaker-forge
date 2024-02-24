import gradio as gr
from model_handler import ModelHandler
from components.speaker_preview_component import SpeechPreviewComponent
from speakers_handler import SpeakersHandler
from utils.utils import get_random_speech_text


class ExploreUI:
    speaker_data = None

    def __init__(self, speakers_handler: SpeakersHandler, model_handler: ModelHandler):
        self.model_handler = model_handler
        self.speakers_handler = speakers_handler

    def createIU(self):
        gr.Markdown(
            value="_Explore the contents of the XTTS speakers file._",
            elem_classes=["section-description"]
        )

        load_speakers_btn = gr.Button("Load Speakers")

        with gr.Group(visible=False) as speaker_group:
            with gr.Row():
                speaker_select = gr.Dropdown(
                    label="Speaker",
                    choices=[],
                    scale=3
                )

        (audio_preview_group,
         audio_player,
         speech_input_textbox,
         generate_speech_btn) = SpeechPreviewComponent()

        # Setup the button click events
        speaker_select.change(
            self.reset_audio_player,
            inputs=[],
            outputs=[audio_player]
        )

        load_speakers_btn.click(
            self.load_speaker_data,
            inputs=None,
            outputs=[
                speaker_group,
                audio_preview_group,
                speaker_select
            ]
        )

        generate_speech_btn.click(
            self.generate_speech,
            inputs=[speaker_select, speech_input_textbox],
            outputs=[
                audio_preview_group,
                generate_speech_btn,
                audio_player
            ]
        ).then(
            self.do_inference,
            inputs=[speaker_select, speech_input_textbox],
            outputs=[generate_speech_btn, audio_player]
        )

    def load_speaker_data(self):
        speakers = self.speakers_handler.get_speaker_names()
        return [
            gr.Group(visible=True),
            gr.Group(visible=True),
            gr.Dropdown(
                label="Speaker",
                choices=speakers,
                visible=True,
                value=speakers[0],
                interactive=True
            )
        ]

    def generate_speech(self, speaker, speech_text):
        print(f"Generate speech for {speaker} with text: {speech_text}")

        return [
            gr.Group(visible=True),
            gr.Button(interactive=False),
            gr.Audio(value=None)
        ]

    def do_inference(self, speaker, speech_text):

        print(f"Running inference for {speaker} with text: {speech_text}")
        self.speaker_data = self.speakers_handler.get_speaker_data(speaker)

        gpt_cond_latent = self.speaker_data['gpt_cond_latent']
        speaker_embedding = self.speaker_data['speaker_embedding']

        wav_file = self.model_handler.run_inference(
            "en", speech_text, gpt_cond_latent, speaker_embedding)

        return [
            gr.Button(interactive=True),
            gr.Audio(value=wav_file)
        ]

    def reset_audio_player(self):
        return gr.Audio(value=None)
