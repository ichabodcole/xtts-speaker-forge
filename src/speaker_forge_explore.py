import gradio as gr
from speakers_handler import SpeakersHandler
from model_handler import ModelHandler


class SpeakerForgeExplore:
    def __init__(self, speakers_handler: SpeakersHandler, model_handler: ModelHandler):
        self.speakers_handler = speakers_handler
        self.model_handler = model_handler

    def load_speaker_data(self):
        speakers = self.speakers_handler.get_speaker_names()
        return [
            gr.Group(visible=True),
            gr.Dropdown(label="Speaker", choices=speakers, visible=True,
                        value=speakers[0], interactive=True)
        ]

    def generate_speech(self, speaker, speech_text):
        print(f"Generate speech for {speaker} with text: {speech_text}")

        return [
            gr.Group(visible=True),
            gr.Markdown(visible=True),
            gr.Button(interactive=False),
            gr.Audio(visible=False)
        ]

    def do_inference(self, speaker, speech_text):
        print(f"Running inference for {speaker} with text: {speech_text}")
        speaker_data = self.speakers_handler.get_speaker_data(speaker)

        gpt_cond_latent = speaker_data['gpt_cond_latent']
        speaker_embedding = speaker_data['speaker_embedding']

        wav_file = self.model_handler.run_inference(
            "en", speech_text, gpt_cond_latent, speaker_embedding)

        return [
            gr.Markdown(visible=False),
            gr.Button(interactive=True),
            gr.Audio(value=wav_file, visible=True)
        ]
