import gradio as gr
from common_ui import validate_file_uploader, validate_text_box
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler
from utils.utils import get_random_speech_text


class CreateUI:
    gpt_cond_latent = None
    speaker_embedding = None

    def __init__(self, speakers_handler: SpeakersHandler, model_handler: ModelHandler):
        self.model_handler = model_handler
        self.speakers_handler = speakers_handler

    def createUI(self):
        gr.Markdown(
            value="_Create a new speaker from one or more reference wavs/mp3s._",
            elem_classes=["section-description"]
        )

        with gr.Group() as speaker_upload_group:
            file_uploader = gr.File(
                label="Upload Speaker wavs or mp3s",
                type="filepath",
                file_count="multiple",
                file_types=["wav", "mp3"],
                interactive=True
            )

            create_speaker_embedding_btn = gr.Button(
                "Create Speaker Embedding",
                interactive=False
            )

            file_uploader.change(
                validate_file_uploader,
                inputs=[file_uploader],
                outputs=create_speaker_embedding_btn
            )

        speaker_embedding_text = gr.Markdown(
            value="### _Creating speaker embedding, try counting some sheep..._",
            visible=False,
            elem_classes=["processing-text"]
        )

        with gr.Group(visible=False) as generate_speech_group:
            # Get a random item from the speech_input_
            input_text = get_random_speech_text()

            speech_textbox = gr.Textbox(
                input_text,
                label="What should I say?",
                placeholder="Type something...",
                lines=3,
                interactive=True
            )

            preview_speaker_btn = gr.Button("Preview Speaker Voice")

            speech_textbox.change(
                validate_text_box,
                inputs=[speech_textbox],
                outputs=preview_speaker_btn
            )

        with gr.Group(visible=False) as speaker_audio_group:
            speaker_audio_messages = gr.Markdown(
                value="### _Calculating the \"Slurp of the Gradients\" (my favorite movie)..._",
                elem_classes=["processing-text"]
            )

            speaker_audio_player = gr.Audio(
                value=None,
                format="wav",
                interactive=False,
                show_download_button=True
            )

        with gr.Group(visible=False) as save_group:
            speaker_name_textbox = gr.Textbox(
                label="Speaker Name",
                placeholder="Enter a unique speaker name and save it to the speaker file.",
                interactive=True
            )

            save_speaker_btn = gr.Button("Save Speaker", interactive=False)

            speaker_name_textbox.change(
                validate_text_box,
                inputs=[speaker_name_textbox],
                outputs=save_speaker_btn
            )

        # Save group text messages
        save_group_messages = gr.Markdown(
            value="### _Speaker saved successfully!_",
            visible=False
        )

        # Setup Events

        # Extracts the speaker embedding from the uploaded audio, then displays the audio player group, but hiding the audio player
        create_speaker_embedding_btn.click(
            lambda: [
                gr.Markdown(visible=True),
                gr.Button(interactive=False),
                gr.Group(visible=False),
                gr.Group(visible=False),
                gr.Group(visible=False)],
            outputs=[
                speaker_embedding_text,
                create_speaker_embedding_btn,
                generate_speech_group,
                speaker_audio_group,
                save_group
            ],
        ).then(
            self.get_speaker_embedding,
            inputs=[file_uploader],
            outputs=[
                speaker_embedding_text,
                generate_speech_group,
                speaker_audio_player
            ]
        )

        # Generates the speech from the speaker embedding and the text,
        preview_speaker_btn.click(
            self.generate_speech,
            inputs=[speaker_name_textbox],
            outputs=[
                speaker_audio_group,
                speaker_audio_messages,
                speaker_audio_player,
                preview_speaker_btn,
                save_group
            ]
        ).then(
            self.do_inference,
            inputs=[speech_textbox],
            outputs=[
                speaker_audio_messages,
                preview_speaker_btn,
                speaker_audio_player,
                save_group
            ]
        )

        save_speaker_btn.click(
            self.save_speaker,
            inputs=[speaker_name_textbox],
            outputs=save_group_messages
        )

    def get_speaker_embedding(self, wav_files):
        gpt_cond_latent, speaker_embedding = self.model_handler.extract_speaker_embedding(
            wav_files)

        self.gpt_cond_latent = gpt_cond_latent
        self.speaker_embedding = speaker_embedding

        # speaker_embedding_text
        # generate_group,
        # speaker_audio_player
        return [
            gr.Markdown(visible=False),
            gr.Group(visible=True),
            gr.Audio(visible=False)
        ]

    def generate_speech(self, speech_text):
        print(f"Generate speech with text: {speech_text}")

        # speaker_audio_group,
        # speaker_audio_messages,
        # speaker_audio_player,
        # preview_speaker_btn,
        # save_group
        return [
            gr.Group(visible=True),
            gr.Markdown(visible=True),
            gr.Audio(visible=False),
            gr.Button(interactive=False),
            gr.Group(visible=False)
        ]

    def do_inference(self, speech_text):
        print(f"Running inference with text: {speech_text}")
        wav_file = "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars3.wav"

        if (self.gpt_cond_latent is None or self.speaker_embedding is None):
            print("Speaker embeddings are not set")
            return

        wav_file = self.model_handler.run_inference(
            "en", speech_text, self.gpt_cond_latent, self.speaker_embedding)

        # speaker_audio_messages,
        # preview_speaker_btn,
        # speaker_audio_player,
        # save_group
        return [
            gr.Markdown(visible=False),
            gr.Button(interactive=True),
            gr.Audio(value=wav_file, visible=True),
            gr.Group(visible=True)
        ]

    def save_speaker(self, speaker_name):
        if (speaker_name is None):
            return gr.Markdown(
                value="### _Speaker name is empty! Please enter a unique speaker name._",
                visible=True
            )

        cur_speaker_names = self.speakers_handler.get_speaker_names()
        if speaker_name in cur_speaker_names:
            return gr.Markdown(
                value="### _Speak name already exists! Please enter a unique speaker name._",
                visible=True
            )

        self.speakers_handler.add_speaker(
            speaker_name, self.gpt_cond_latent, self.speaker_embedding)

        self.speakers_handler.save_speaker_file()

        # save_group_messages
        return gr.Markdown(
            value=f"### _Speaker \"{speaker_name}\" added successfully!_",
            visible=True
        )
