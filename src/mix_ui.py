import random
import time
import gradio as gr
from common_ui import validate_file_uploader, validate_text_box
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler
from typing import List
from random import choice, choices, randrange
from constants import speech_input_defaults
from types_module import EmbeddingPair, SliderList, SpeakerEmbedding, SpeakerNameList


class MixUI:
    speaker_name_list: SpeakerNameList = []
    speaker_control_list: SliderList = []
    speaker_weights = []
    speaker_embedding: SpeakerEmbedding = None
    is_spicy = False

    def __init__(self, speakers_handler: SpeakersHandler, model_handler: ModelHandler):
        self.speakers_handler = speakers_handler
        self.model_handler = model_handler
        self.speaker_name_list = self.speakers_handler.get_speaker_names()

    def createUI(self):
        gr.Markdown(
            value="_Mix and match speakers like a young Voicetor Frankenspeaker_",
            elem_classes=["section-description"]
        )

        load_speakers_btn = gr.Button("Load Speakers")

        with gr.Group(visible=False) as speaker_group:
            with gr.Row():
                speaker_select = gr.Dropdown(
                    label="Speaker",
                    choices=[],
                    scale=3,
                    multiselect=True,
                    interactive=True
                )

                feeling_spicy_btn = gr.Button("Feeling Spicy?", scale=1)

        with gr.Group(visible=False) as speaker_control_group:
            with gr.Row():
                for speaker_name in self.speaker_name_list:
                    speaker_control = gr.Slider(
                        label=speaker_name,
                        minimum=0,
                        maximum=10,
                        step=0.1,
                        value=1,
                        interactive=True,
                        visible=False,
                        elem_classes="slider-ctrl"
                    )

                    label = gr.Label(speaker_name, visible=False)

                    speaker_control.input(
                        self.handle_speaker_slider_change,
                        inputs=[label, speaker_control],
                        outputs=[]
                    )

                    self.speaker_control_list.append(speaker_control)

            create_speaker_btn = gr.Button("Create Franken-Speaker™")

            # speaker_control_message = gr.Markdown(
            #     value="### _Creating Franken-Speaker™... (queue ominous thunder and lighting strikes)_",
            #     elem_classes=['processing-text'],
            #     visible=True
            # )

        with gr.Group(visible=False) as speaker_preview_group:

            # speaker_preview_message = gr.Markdown(
            #     value="### _Generating speech, commence sitting at the edge of your seat..._",
            #     elem_classes=['processing-text'],
            #     visible=True
            # )

            speaker_audio_player = gr.Audio(
                interactive=False,
                show_download_button=True,
            )

            speaker_text_textbox = gr.Textbox(
                label="What should I say?",
                placeholder="Enter text to speak",
                lines=3,
                interactive=True,
                value=choice(speech_input_defaults)
            )

            generate_speech_btn = gr.Button("Generate Speech")

        with gr.Group(visible=False) as speaker_save_group:
            with gr.Row():
                speaker_name_textbox = gr.Textbox(
                    label="Name your Franken-Speaker™",
                    placeholder="Enter Franken-Speaker™ name",
                    interactive=True,
                    scale=3
                )

                save_speaker_btn = gr.Button("Save Franken-Speaker™", scale=1)

        # speaker_save_message = gr.Markdown(
        #     value="### _Speaker Saved!_",
        #     elem_classes=['processing-text'],
        #     visible=True
        # )

        # Event Handlers
        load_speakers_btn.click(
            self.handle_load_speaker_click,
            inputs=[],
            outputs=[
                speaker_group,
                speaker_select
            ]
        )

        speaker_select.change(
            self.update_speaker_controls,
            inputs=[speaker_select],
            outputs=self.speaker_control_list
        )

        speaker_select.change(
            self.handle_speaker_select_change,
            inputs=[speaker_select],
            outputs=[
                speaker_control_group,
                speaker_preview_group,
                speaker_save_group
            ]
        )

        feeling_spicy_btn.click(
            self.handle_spicy_click,
            inputs=[],
            outputs=speaker_select
        )

        create_speaker_btn.click(
            self.handle_create_speaker_click,
            inputs=[],
            outputs=[
                speaker_audio_player,
                speaker_save_group,
                speaker_preview_group
            ]
        ).then(
            self.create_speaker_from_mix,
            inputs=[],
            outputs=speaker_preview_group
        )

        generate_speech_btn.click(
            self.generate_speech_click,
            inputs=[],
            outputs=[
                speaker_audio_player,
                speaker_save_group
            ]
        ).then(
            self.do_inference,
            inputs=[speaker_text_textbox],
            outputs=[
                speaker_audio_player,
                speaker_save_group
            ]
        )

        speaker_name_textbox.change(
            validate_text_box,
            inputs=[speaker_name_textbox],
            outputs=[save_speaker_btn]
        )

        save_speaker_btn.click(
            self.handle_save_speaker_click,
            inputs=[speaker_name_textbox],
            outputs=[]
        )

    # Helpers
    def update_speaker_controls(self, speaker_select):
        next_list: SliderList = []

        for speaker_control in self.speaker_control_list:
            value = round(
                random.uniform(1, 10), 1
            ) if self.is_spicy else speaker_control.value or 1
            speaker_name = speaker_control.label

            if speaker_name in speaker_select:
                slider = gr.Slider(
                    label=speaker_name,
                    visible=True,
                    value=value
                )
            else:
                slider = gr.Slider(visible=False, value=0)

            next_list.append(slider)

        self.is_spicy = False

        return next_list

    def handle_load_speaker_click(self):
        self.speaker_name_list = self.speakers_handler.get_speaker_names()

        return [
            gr.Group(visible=True),
            gr.Dropdown(
                choices=self.speaker_name_list,
                visible=True
            )
        ]

    def handle_speaker_select_change(self, selected_speakers):
        is_valid_count = len(selected_speakers) > 1

        self.speaker_weights = []
        for speaker in selected_speakers:
            self.speaker_weights.append({
                "speaker": speaker,
                "weight": 1
            })

        return [
            gr.Group(visible=is_valid_count),
            gr.Group(visible=False),
            gr.Group(visible=False)
        ]

    def handle_spicy_click(self):
        self.is_spicy = True
        speaker_select_count = randrange(2, 6)
        speakers = choices(self.speaker_name_list, k=speaker_select_count)
        return gr.Dropdown(value=speakers)

    def handle_speaker_slider_change(self, slider_label, slider_value):

        def speaker_filter(speaker_weight):
            return False if speaker_weight["speaker"] == slider_label else True

        self.speaker_weights = list(
            filter(speaker_filter, self.speaker_weights))

        self.speaker_weights.append(
            {"speaker": slider_label, "weight": slider_value})

    def handle_create_speaker_click(self):
        return [
            gr.Audio(value=None),
            gr.Group(visible=False),
            gr.Group(visible=True)
        ]

    def create_speaker_from_mix(self):

        print("mix from speaker_weights", self.speaker_weights)

        self.speaker_embedding = self.speakers_handler.create_speaker_embedding_from_mix(
            self.speaker_weights)

        return gr.Group(visible=True)

    def generate_speech_click(self):
        if (self.speaker_embedding is None):
            # Implement UI error message
            pass

        return [
            gr.Audio(value=None),
            gr.Group(visible=False)
        ]

    def handle_save_speaker_click(self, speaker_name):
        gpt_cond_latent = self.speaker_embedding["gpt_cond_latent"]
        speaker_embedding = self.speaker_embedding["speaker_embedding"]

        self.speakers_handler.add_speaker(
            speaker_name, gpt_cond_latent, speaker_embedding)

    def do_inference(self, speech_input_text):
        wav_file = "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars3.wav"

        wav_file = self.model_handler.run_inference(
            'en',
            speech_input_text,
            self.speaker_embedding["gpt_cond_latent"],
            self.speaker_embedding["speaker_embedding"],
            self.speaker_weights_to_file_name()
        )

        return [gr.Audio(value=wav_file), gr.Group(visible=True)]

    # Converts speaker weights to a file name string
    def speaker_weights_to_file_name(self):
        file_name = ""
        for speaker in self.speaker_weights:
            file_name += f"{speaker['speaker']}_{speaker['weight']}_"
        return file_name
