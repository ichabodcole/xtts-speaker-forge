import random
import gradio as gr
from common_ui import validate_text_box
from components.textbox_submit_component import TextboxSubmitComponent
from constants.common import MAX_SPEAKER_CONTROL_COUNT
from model_handler import ModelHandler
from components.speaker_preview_component import SpeechPreviewComponent
from speakers_handler import SpeakersHandler
from random import choices, randrange
from types_module import SliderList, SpeakerEmbedding, SpeakerNameList, SpeakerWeightsList

SLIDER_MAX = 2
SLIDER_MIN = 0
SLIDER_STEP = 0.1
UNASSIGNED = "UNASSIGNED"


class MixUI:
    speaker_name_list: SpeakerNameList = []
    speaker_control_list: SliderList = []
    speaker_weights: SpeakerWeightsList = []
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
                for idx in list(range(0, MAX_SPEAKER_CONTROL_COUNT)):
                    speaker_name = self.speaker_name_list[idx] if idx < len(
                        self.speaker_name_list) else UNASSIGNED

                    speaker_control = gr.Slider(
                        label=speaker_name,
                        minimum=SLIDER_MIN,
                        maximum=SLIDER_MAX,
                        step=SLIDER_STEP,
                        value=1,
                        interactive=True,
                        visible=False,
                        elem_classes="slider-ctrl",
                        elem_id=str(idx)
                    )

                    self.speaker_control_list.append(speaker_control)

            with gr.Row():
                randomize_speaker_weights_btn = gr.Button("Randomize Weights")
                reset_speaker_weights_btn = gr.Button("Reset Weights")

        # SPEAKER PREVIEW COMPONENT
        (audio_preview_group,
         audio_player,
         speech_input_textbox,
         generate_speech_btn) = SpeechPreviewComponent()

        # SAVE SPEAKER COMPONENT
        (speaker_save_group,
         speaker_name_textbox,
         save_speaker_btn,
         save_notification_text) = TextboxSubmitComponent(
            textbox_label="Name your Franken-Speaker™",
            button_label="Save Franken-Speaker™",
            placeholder="Enter Franken-Speaker™ name"
        )

        # Event Handlers
        for speaker_control in self.speaker_control_list:
            speaker_control.input(
                self.handle_speaker_slider_change,
                inputs=[speaker_control],
                outputs=[]
            ).then(
                lambda: [gr.Audio(value=None), gr.Group(visible=False)],
                inputs=[],
                outputs=[audio_player, speaker_save_group]
            )

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
        ).then(
            self.handle_speaker_select_change,
            inputs=[speaker_select],
            outputs=[
                speaker_control_group,
                audio_preview_group,
                audio_player,
                speaker_save_group
            ]
        )

        feeling_spicy_btn.click(
            self.handle_spicy_click,
            inputs=[],
            outputs=speaker_select
        )

        randomize_speaker_weights_btn.click(
            self.handle_randomize_speaker_weights_click,
            inputs=[speaker_select],
            outputs=self.speaker_control_list
        ).then(
            lambda: gr.Audio(value=None),
            inputs=[],
            outputs=audio_player
        )

        reset_speaker_weights_btn.click(
            self.handle_reset_speaker_weights_click,
            inputs=[speaker_select],
            outputs=self.speaker_control_list
        )

        generate_speech_btn.click(
            self.handle_generate_speech_click,
            inputs=[],
            outputs=[
                audio_player,
                speaker_save_group
            ]
        ).then(
            self.do_inference,
            inputs=[speech_input_textbox],
            outputs=[
                audio_player,
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
            outputs=[save_notification_text]
        )

    # Helpers
    def update_speaker_controls(self, speaker_select):
        next_list: SliderList = []

        unassigned_speakers = self.get_speakers_not_in_speaker_control_list(
            speaker_select)

        self.speaker_weights = self.filter_speaker_weights(speaker_select)

        for speaker_control in self.speaker_control_list:
            control_label = speaker_control.label

            if control_label in speaker_select:
                speaker_weight = self.get_speaker_weight(control_label)
                value = self.get_spicy_value() if self.is_spicy else speaker_weight
                self.update_speaker_weights(control_label, value)

                slider = gr.Slider(
                    label=control_label,
                    visible=True,
                    value=value
                )
            else:
                if len(unassigned_speakers) > 0 and control_label == UNASSIGNED:
                    speaker_name = unassigned_speakers.pop()
                    value = self.get_spicy_value() if self.is_spicy else 1
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

        return [
            gr.Group(visible=is_valid_count),
            gr.Group(visible=is_valid_count),
            gr.Audio(value=None),
            gr.Group(visible=False)
        ]

    def handle_spicy_click(self):
        self.is_spicy = True
        speaker_select_count = randrange(2, 6)
        speakers = choices(self.speaker_name_list, k=speaker_select_count)
        return gr.Dropdown(value=speakers)

    def handle_speaker_slider_change(self, slider_value, evt: gr.EventData):
        slider_index = evt.target.elem_id
        speaker_name = self.speaker_name_list[int(slider_index)]

        self.update_speaker_weights(speaker_name, slider_value)

    def handle_generate_speech_click(self):
        self.speaker_embedding = self.speakers_handler.create_speaker_embedding_from_mix(
            self.speaker_weights)

        print("generating speech with speaker_weights", self.speaker_weights)

        return [
            gr.Audio(value=None),
            gr.Group(visible=False)
        ]

    def handle_randomize_speaker_weights_click(self, selected_speakers: SpeakerNameList):
        next_slider_list: SliderList = []
        self.randomize_speaker_weights()

        for speaker_control in self.speaker_control_list:
            speaker_name = speaker_control.label

            if speaker_name in selected_speakers:
                speaker_weight = self.get_speaker_weight(speaker_name)
                slider = gr.Slider(
                    label=speaker_name,
                    visible=True,
                    value=speaker_weight
                )
            else:
                slider = gr.Slider(visible=False, value=0)

            next_slider_list.append(slider)

        return next_slider_list

    def handle_reset_speaker_weights_click(self, selected_speakers: SpeakerNameList):
        next_slider_list: SliderList = []

        for speaker_control in self.speaker_control_list:
            speaker_name = speaker_control.label

            if speaker_name in selected_speakers:
                slider = gr.Slider(
                    label=speaker_name,
                    visible=True,
                    value=1
                )
            else:
                slider = gr.Slider(visible=False, value=0)

            next_slider_list.append(slider)

        return next_slider_list

    def handle_save_speaker_click(self, speaker_name):
        gpt_cond_latent = self.speaker_embedding["gpt_cond_latent"]
        speaker_embedding = self.speaker_embedding["speaker_embedding"]

        self.speakers_handler.add_speaker(
            speaker_name, gpt_cond_latent, speaker_embedding)

        self.speakers_handler.save_speaker_file()

        return gr.Markdown(visible=True)

    def do_inference(self, speech_input_text):
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

    def get_speaker_weight(self, speaker_name: str) -> float:
        return next((speaker_weight["weight"] for speaker_weight in self.speaker_weights if speaker_weight["speaker"] == speaker_name), 1.0)

    def filter_speaker_weights(self, speaker_list: SpeakerNameList) -> SpeakerWeightsList:
        return list(filter(lambda speaker_weight: speaker_weight["speaker"] in speaker_list, self.speaker_weights))

    def update_speaker_weights(self, speaker_name: str, weight: float):
        # If speaker already exists, update weight
        for speaker_weight in self.speaker_weights:
            if speaker_weight["speaker"] == speaker_name:
                speaker_weight["weight"] = weight
                return self.speaker_weights

        # Otherwise, add new speaker
        self.speaker_weights.append(
            {"speaker": speaker_name, "weight": weight})

        return self.speaker_weights

    def get_spicy_value(self):
        return round(random.uniform(max(SLIDER_MIN, 0.1), SLIDER_MAX), 1)

    def randomize_speaker_weights(self):
        for speaker_weight in self.speaker_weights:
            speaker_weight["weight"] = self.get_spicy_value()

    def is_speaker_in_speaker_control_list(self, speaker_name: str):
        return next((True for speaker_control in self.speaker_control_list if speaker_control.label == speaker_name), False)

    def has_speakers_not_in_speaker_control_list(self, speaker_list: SpeakerNameList):
        return next((True for speaker_name in speaker_list if not self.is_speaker_in_speaker_control_list(speaker_name)), False)

    def get_speakers_not_in_speaker_control_list(self, speaker_list: SpeakerNameList):
        return list(filter(lambda speaker_name: not self.is_speaker_in_speaker_control_list(speaker_name), speaker_list))

    def assign_new_speaker_to_control_list(self, speaker_name: str):
        next_list: SliderList = []
        for speaker_control in self.speaker_control_list:
            if speaker_control.label is UNASSIGNED:
                next_list.append(
                    gr.Slider(label=speaker_name, visible=True, value=1))
            else:
                next_list.append(gr.Slider())

        return next_list
