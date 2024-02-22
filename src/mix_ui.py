import time
import gradio as gr
from common_ui import validate_file_uploader, validate_text_box
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler
from typing import List
from random import choice, choices, randrange
from constants import speech_input_defaults


class MixUI:
    speaker_names = None
    speaker_control_list = []
    is_spicy = False

    def __init__(self, speakers_handler: SpeakersHandler, model_handler: ModelHandler):
        self.speakers_handler = speakers_handler
        self.model_handler = model_handler

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
                    interactive=True,
                )

                feeling_spicy_btn = gr.Button("Feeling Spicy?", scale=1)

        with gr.Group(visible=False) as speaker_control_group:
            with gr.Row():

                for speaker in self.load_speaker_names():
                    speaker = gr.Slider(
                        label=speaker,
                        minimum=0,
                        maximum=10,
                        step=1,
                        value=1,
                        interactive=True,
                        visible=False,
                        elem_classes="speaker-mix-slider")

                    self.speaker_control_list.append(speaker)

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
                placeholder="Enter text to speak",
                lines=3,
                interactive=True,
                value=choice(speech_input_defaults)
            )

            generate_speech_btn = gr.Button("Generate Speech")

        with gr.Group(visible=False) as speaker_save_group:
            with gr.Row():
                speaker_name_textbox = gr.Textbox(
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
            inputs=[speaker_select],
            outputs=speaker_preview_group
        )

        generate_speech_btn.click(
            self.generate_speech_click,
            inputs=[speaker_text_textbox],
            outputs=[
                speaker_audio_player,
                speaker_save_group
            ]
        ).then(
            self.do_inference,
            inputs=[],
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
    def update_speaker_controls(self, selected_speakers):
        next_list = []
        print(self.is_spicy)
        for speaker_control in self.speaker_control_list:
            value = randrange(1, 10) if self.is_spicy else 1

            if speaker_control.label in selected_speakers:
                next_list.append(gr.Slider(visible=True, value=value))
            else:
                next_list.append(gr.Slider(visible=False, value=0))

        self.is_spicy = False

        return next_list

    def handle_load_speaker_click(self):
        self.load_speaker_names()

        return [
            gr.Group(visible=True),
            gr.Dropdown(
                choices=self.speaker_names,
                visible=True
            )
        ]

    def handle_speaker_select_change(self, selected_speakers):
        is_valid_count = len(selected_speakers) > 1

        return [
            gr.Group(visible=is_valid_count),
            gr.Group(visible=False),
            gr.Group(visible=False)
        ]

    def handle_spicy_click(self):
        self.is_spicy = True
        speaker_names = self.load_speaker_names()
        speaker_select_count = randrange(2, 6)
        speakers = choices(speaker_names, k=speaker_select_count)

        return gr.Dropdown(value=speakers)

    def handle_create_speaker_click(self):
        return [
            gr.Audio(value=None),
            gr.Group(visible=False),
            gr.Group(visible=True)
        ]

    def create_speaker_from_mix(self, selected_speakers):
        speaker_weights = []
        for speaker_control in self.speaker_control_list:
            if speaker_control.visible:
                speaker_value_pair = [
                    speaker_control.label,
                    speaker_control.value
                ]

                speaker_weights.append(speaker_value_pair)

        time.sleep(3)

        # self.model_handler

        return gr.Group(visible=True)

    def generate_speech_click(self, speech_input_text):
        print(speech_input_text)

        return [
            gr.Audio(value=None),
            gr.Group(visible=False)
        ]

    def handle_save_speaker_click(self):
        pass

    def do_inference(self):
        wav_file = "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars3.wav"

        time.sleep(3)

        return [gr.Audio(value=wav_file), gr.Group(visible=True)]

    def load_speaker_names(self):
        if (not self.speaker_names):
            self.speaker_names = self.speakers_handler.get_speaker_names()

        return self.speaker_names
