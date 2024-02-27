import random
import gradio as gr
from common_ui import validate_text_box
from components.section_description_component import SectionDescriptionComponent
from components.textbox_submit_component import TextboxSubmitComponent
from constants.common import MAX_SPEAKER_CONTROL_COUNT
from content_handler import ContentHandler
from forge_base_view import ForgeBaseView
from model_handler import ModelHandler
from components.speaker_preview_component import SpeechPreviewComponent
from speakers_handler import SpeakersHandler
from random import choices, randrange
from types_module import SliderList, SpeakerEmbedding, SpeakerNameList, SpeakerWeightsList
from utils.utils import format_notification

SLIDER_MAX = 2
SLIDER_MIN = 0
SLIDER_STEP = 0.1
UNASSIGNED = "UNASSIGNED"


class ForgeMixView(ForgeBaseView):
    speaker_name_list: SpeakerNameList = []
    speaker_control_list: SliderList = []
    speaker_weights: SpeakerWeightsList = []
    speaker_embedding: SpeakerEmbedding = None
    is_spicy = False
    section_content: dict
    common_content: dict

    def __init__(
        self,
        speaker_handler: SpeakersHandler,
        model_handler: ModelHandler,
        content_handler: ContentHandler
    ):
        super().__init__(speaker_handler, model_handler, content_handler)
        self.speaker_name_list = self.speakers_handler.get_speaker_names()
        self.section_content = self.content_handler.get_section_content("mix")
        self.common_content = self.content_handler.get_common_content()

    def init_ui(self):

        section_description = SectionDescriptionComponent(
            value=self.section_content.get("section_description"))

        load_speakers_btn = gr.Button(
            self.common_content.get("load_speakers_btn_label"))

        with gr.Group(visible=False) as speaker_group:
            with gr.Row():
                speaker_select = gr.Dropdown(
                    label=self.common_content.get(
                        "select_speakers_dropdown_label"),
                    choices=[],
                    scale=3,
                    multiselect=True,
                    interactive=True
                )

                feeling_spicy_btn = gr.Button(
                    value=self.section_content.get("feeling_spicy_btn_label"), scale=1)

        with gr.Group(visible=False) as speaker_control_group:
            with gr.Row():
                for idx in list(range(0, MAX_SPEAKER_CONTROL_COUNT)):
                    speaker_name = self.get_speaker_name_by_index(idx)

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
                randomize_speaker_weights_btn = gr.Button(
                    value=self.section_content.get("randomize_weights_btn_label"))
                reset_speaker_weights_btn = gr.Button(
                    value=self.section_content.get("reset_weights_btn_label"))

        # SPEAKER PREVIEW COMPONENT
        (audio_preview_group,
         audio_player,
         speech_input_textbox,
         generate_speech_btn) = SpeechPreviewComponent(self.content_handler.get_common_content())

        # SAVE SPEAKER COMPONENT
        (speaker_save_group,
         speaker_name_textbox,
         save_speaker_btn,
         save_notification_text) = TextboxSubmitComponent(
            textbox_label=self.common_content.get("save_speaker_name_label"),
            button_label=self.common_content.get("save_speaker_btn_label"),
            placeholder=self.common_content.get("save_speaker_placeholder"),
            notification_message=self.common_content.get(
                "save_speaker_success_msg")
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
                speaker_save_group,
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
                speaker_save_group,
                save_notification_text
            ]
        ).then(
            self.lock_ui,
            outputs=[
                speaker_select,
                feeling_spicy_btn,
                randomize_speaker_weights_btn,
                reset_speaker_weights_btn
            ]
        ).then(
            self.disable_control_list,
            inputs=[speaker_select],
            outputs=self.speaker_control_list
        ).then(
            self.do_inference,
            inputs=[speech_input_textbox],
            outputs=[
                generate_speech_btn,
                audio_player,
                speaker_save_group,
            ]
        ).then(
            self.unlock_ui,
            outputs=[
                speaker_select,
                feeling_spicy_btn,
                randomize_speaker_weights_btn,
                reset_speaker_weights_btn
            ]
        ).then(
            self.enable_control_list,
            inputs=[speaker_select],
            outputs=self.speaker_control_list
        )

        speaker_name_textbox.change(
            validate_text_box,
            inputs=[speaker_name_textbox],
            outputs=save_speaker_btn
        )

        save_speaker_btn.click(
            self.handle_save_speaker_click,
            inputs=[speaker_name_textbox],
            outputs=save_notification_text
        ).then(
            self.handle_load_speaker_click,
            outputs=[
                speaker_group,
                speaker_select
            ]
        )

    # Helpers
    def update_speaker_controls(self, speaker_select):
        next_list: SliderList = []

        self.speaker_weights = self.filter_speaker_weights(speaker_select)

        for idx, speaker_control in enumerate(self.speaker_control_list):
            speaker_name = self.get_speaker_name_by_index(idx)

            if speaker_name in speaker_select:
                speaker_weight = self.get_speaker_weight(speaker_name)
                value = self.get_spicy_value() if self.is_spicy else speaker_weight
                self.update_speaker_weights(speaker_name, value)

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
            gr.Group(visible=False),
            gr.Markdown(visible=False)
        ]

    def handle_randomize_speaker_weights_click(self, selected_speakers: SpeakerNameList):
        next_slider_list: SliderList = []
        self.randomize_speaker_weights()

        for idx, speaker_control in enumerate(self.speaker_control_list):
            speaker_name = self.get_speaker_name_by_index(idx)

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

        for idx, speaker_control in enumerate(self.speaker_control_list):
            speaker_name = self.get_speaker_name_by_index(idx)

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

        # self.speakers_handler.save_speaker_file()

        return gr.Markdown(
            value=format_notification(
                f"Speaker \"{speaker_name}\" added successfully!")
        )

    def do_inference(self, speech_input_text):
        wav_file = self.model_handler.run_inference(
            'en',
            speech_input_text,
            self.speaker_embedding["gpt_cond_latent"],
            self.speaker_embedding["speaker_embedding"],
            self.speaker_weights_to_file_name()
        )

        return [
            gr.Button(interactive=True),
            gr.Audio(value=wav_file),
            gr.Group(visible=True)
        ]

    def lock_ui(self):
        return [
            gr.Dropdown(interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False)
        ]

    def disable_control_list(self, selected_speakers: SpeakerNameList):
        next_slider_list: SliderList = []

        for idx, speaker_control in enumerate(self.speaker_control_list):
            speaker_name = self.get_speaker_name_by_index(idx)

            if speaker_name in selected_speakers:
                slider = gr.Slider(
                    interactive=False
                )
            else:
                slider = gr.Slider(visible=False, value=0)

            next_slider_list.append(slider)

        return next_slider_list

    def unlock_ui(self):
        return [
            gr.Dropdown(interactive=True),
            gr.Button(interactive=True),
            gr.Button(interactive=True),
            gr.Button(interactive=True)
        ]

    def enable_control_list(self, selected_speakers: SpeakerNameList):
        next_slider_list: SliderList = []

        for idx, speaker_control in enumerate(self.speaker_control_list):
            speaker_name = self.get_speaker_name_by_index(idx)

            if speaker_name in selected_speakers:
                slider = gr.Slider(
                    interactive=True
                )
            else:
                slider = gr.Slider(visible=False, value=0)

            next_slider_list.append(slider)

        return next_slider_list

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

    def get_speaker_name_by_index(self, index: int):
        return self.speaker_name_list[index] if index < len(self.speaker_name_list) else UNASSIGNED
