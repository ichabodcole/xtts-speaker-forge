import gradio as gr
from model_handler import ModelHandler
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

                remove_speaker_btn = gr.Button("Remove Speaker", scale=1)

                remove_speaker_btn.click(
                    self.remove_speaker,
                    inputs=[speaker_select],
                    outputs=[speaker_select]
                )

            # Get a random item from the speech_input_
            input_text = get_random_speech_text()

            speech_text_box = gr.Textbox(
                input_text,
                label="Speech Text",
                placeholder="Type something...",
                lines=3,
                interactive=True
            )

            generate_speech_btn = gr.Button(
                "Generate Speech")

        with gr.Group(visible=False) as processing_group:
            processing_text = gr.Markdown(
                value="### _Doing the maths n' stuff, please be patient..._",
                elem_classes=["processing-text"]
            )

            audio_player = gr.Audio(
                value=None, format="wav")

        # Setup the button click events
        load_speakers_btn.click(
            self.load_speaker_data,
            inputs=None,
            outputs=[speaker_group, speaker_select]
        )

        generate_speech_btn.click(
            self.generate_speech,
            inputs=[speaker_select, speech_text_box],
            outputs=[
                processing_group,
                processing_text,
                generate_speech_btn,
                audio_player
            ]
        ).then(
            self.do_inference,
            inputs=[speaker_select, speech_text_box],
            outputs=[processing_text, generate_speech_btn, audio_player]
        )

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
        self.speaker_data = self.speakers_handler.get_speaker_data(speaker)

        gpt_cond_latent = self.speaker_data['gpt_cond_latent']
        speaker_embedding = self.speaker_data['speaker_embedding']

        wav_file = self.model_handler.run_inference(
            "en", speech_text, gpt_cond_latent, speaker_embedding)

        return [
            gr.Markdown(visible=False),
            gr.Button(interactive=True),
            gr.Audio(value=wav_file, visible=True)
        ]

    def remove_speaker(self, speaker_name):
        if (speaker_name is None):
            return gr.Markdown(
                value="### _Speaker name is empty! Please enter a speaker name._",
                visible=True
            )

        self.speakers_handler.remove_speaker(speaker_name)
        self.speakers_handler.save_speaker_file()

        speakers = self.speakers_handler.get_speaker_names()
        return gr.Dropdown(label="Speaker", choices=speakers, visible=True, value=speakers[0], interactive=True)
