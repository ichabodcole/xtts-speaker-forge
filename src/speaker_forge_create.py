import gradio as gr
from speakers_handler import SpeakersHandler
from model_handler import ModelHandler


class SpeakerForgeCreate:
    gpt_cond_latent = None
    speaker_embedding = None

    def __init__(self, speakers_handler: SpeakersHandler, model_handler: ModelHandler):
        self.speakers_handler = speakers_handler
        self.model_handler = model_handler

    def get_speaker_embedding(self, wav_files):
        print(wav_files)
        # gpt_cond_latent, speaker_embedding = self.model_handler.extract_speaker_embedding(
        #     wav_files)

        # self.gpt_cond_latent = gpt_cond_latent
        # self.speaker_embedding = speaker_embedding

        return [
            gr.Group(visible=True),
            gr.Audio(visible=False)
        ]

    def generate_speech(self, speech_text):
        print(f"Generate speech with text: {speech_text}")

        return [gr.Group(visible=True), gr.Markdown(visible=True), gr.Group(visible=False)]

    def do_inference(self, speech_text):
        print(f"Running inference with text: {speech_text}")
        wav_file = "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars3.wav"
        # if (self.gpt_cond_latent is None or self.speaker_embedding is None):
        #     print("Speaker embeddings are not set")
        #     return

        # wav_file = self.model_handler.run_inference(
        #     "en", speech_text, self.gpt_cond_latent, self.speaker_embedding)

        return [
            gr.Markdown(visible=False),
            gr.Button(interactive=True),
            gr.Audio(value=wav_file, visible=True),
            gr.Group(visible=True)
        ]

    def save_speaker(self, speaker_name):
        if (speaker_name is None):
            print("Speaker name is not set")
            return gr.Markdown(
                value="### _Speaker name is empty! Please enter a unique speaker name._",
                visible=True
            )

        cur_speaker_names = self.speakers_handler.get_speaker_names()
        if speaker_name in cur_speaker_names:
            print(f"Speaker: {speaker_name} already exists")
            return gr.Markdown(
                value="### _Speak name already exists! Please enter a unique speaker name._",
                visible=True
            )

        print(f"Save speaker: {speaker_name}")

        # self.speakers_handler.add_speaker(
        #     speaker_name, self.gpt_cond_latent, self.speaker_embedding)

        return gr.Markdown(
            value="### _Speaker added successfully!_",
            visible=True
        )
