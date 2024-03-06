import random
import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from components.textbox_submit_component import TextboxSubmitComponent
from services.content_manager_service import ContentManagerService
from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from components.speaker_preview_component import SpeechPreviewComponent
from services.speaker_manager_service import SpeakerManagerService
from random import randrange
from types_module import SliderList, SpeakerData, SpeakerNameList, SpeakerWeightsList
from utils.utils import format_notification

MAX_SPEAKER_CONTROL_COUNT = 10
MAX_SPICY_SPEAKER_COUNT = 5
SLIDER_MAX = 2
SLIDER_MIN = 0
SLIDER_STEP = 0.1
UNASSIGNED = "UNASSIGNED"


class ForgeMixView(ForgeBaseView):
    speaker_name_list: SpeakerNameList = []
    speaker_control_list: SliderList = []
    speaker_weights: SpeakerWeightsList = []
    speaker_embedding: SpeakerData = None
    is_spicy = False
    section_content: dict
    common_content: dict

    def __init__(
        self,
        speaker_service: SpeakerManagerService,
        model_service: ModelManagerService,
        content_service: ContentManagerService
    ):
        super().__init__(speaker_service, model_service, content_service)
        self.speaker_name_list = self.speaker_service.get_speaker_names()
        self.section_content = self.content_service.get_section_content("mix")
        self.common_content = self.content_service.get_common_content()

    def init_ui(self):

        section_description = SectionDescriptionComponent(
            value=self.section_content.get("section_description"))

        load_speakers_btn = gr.Button(
            self.common_content.get("load_speakers_btn_label"))

        with gr.Column() as ui_container:
            with gr.Group(visible=False) as speaker_select_group:
                with gr.Row():
                    speaker_select = gr.Dropdown(
                        label=self.common_content.get(
                            "select_speakers_dropdown_label"),
                        choices=[],
                        max_choices=MAX_SPEAKER_CONTROL_COUNT,
                        scale=3,
                        multiselect=True,
                        interactive=True
                    )

                    feeling_spicy_btn = gr.Button(
                        value=self.section_content.get("feeling_spicy_btn_label"), scale=1)

            with gr.Group(visible=False) as speaker_control_group:
                with gr.Row():
                    for idx in list(range(0, MAX_SPEAKER_CONTROL_COUNT)):
                        speaker_control = gr.Slider(
                            label=UNASSIGNED,
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
             language_select,
             generate_speech_btn) = SpeechPreviewComponent(self.content_service.get_common_content())

            # SAVE SPEAKER COMPONENT
            (speaker_save_group,
             speaker_name_textbox,
             save_speaker_btn,
             save_notification_text) = TextboxSubmitComponent(
                textbox_label=self.common_content.get(
                    "save_speaker_name_label"),
                button_label=self.common_content.get("save_speaker_btn_label"),
                placeholder=self.common_content.get(
                    "save_speaker_placeholder"),
                notification_message=self.common_content.get(
                    "save_speaker_success_msg")
            )

            # Event Handlers
            for speaker_control in self.speaker_control_list:
                speaker_control.input(
                    self.handle_speaker_slider_change,
                    inputs=[speaker_control, speaker_select],
                    outputs=[]
                ).then(
                    lambda: [gr.Audio(value=None), gr.Group(visible=False)],
                    outputs=[audio_player, speaker_save_group]
                )

            load_speakers_btn.click(
                self.handle_load_speaker_click,
                inputs=[],
                outputs=speaker_select
            ).then(
                lambda: gr.Group(visible=True),
                outputs=speaker_select_group
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
                    audio_preview_group
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
            )

            reset_speaker_weights_btn.click(
                self.handle_reset_speaker_weights_click,
                inputs=[speaker_select],
                outputs=self.speaker_control_list
            )

            gr.on(
                triggers=[
                    randomize_speaker_weights_btn.click,
                    reset_speaker_weights_btn.click,
                    generate_speech_btn.click,
                    speaker_select.change
                ],
                fn=lambda: [gr.Audio(value=None), gr.Group(visible=False)],
                outputs=[audio_player, speaker_save_group]
            )

            # TODO: Clean up this mess
            generate_speech_btn.click(
                self.handle_generate_speech_click,
                inputs=[],
                outputs=ui_container
            ).then(
                self.disable_control_list,
                inputs=[speaker_select],
                outputs=self.speaker_control_list
            ).then(
                self.do_inference,
                inputs=[speech_input_textbox, language_select],
                outputs=[
                    generate_speech_btn,
                    audio_player,
                    ui_container,
                    speaker_save_group
                ]
            ).then(
                self.enable_control_list,
                inputs=[speaker_select],
                outputs=self.speaker_control_list
            )

            save_speaker_btn.click(
                self.handle_save_speaker_click,
                inputs=[speaker_name_textbox],
                outputs=save_notification_text
            ).then(
                self.handle_load_speaker_click,
                outputs=speaker_select
            )

    # Helpers
    def update_speaker_controls(self, selected_speakers):
        self.speaker_weights = self.filter_speaker_weights(selected_speakers)

        def calculate_value(speaker_name: str) -> float:
            value = self.get_spicy_value() if self.is_spicy else self.get_speaker_weight(speaker_name)
            # Side effect: update speaker weights
            self.update_speaker_weights(speaker_name, value)

            return value

        active_slider_props = {
            "visible": True
        }

        inactive_slider_props = {
            "visible": False,
            "value": 0
        }

        next_sliders = self.update_slider_props(
            selected_speakers,
            active_slider_props,
            inactive_slider_props,
            valueFn=calculate_value
        )

        self.is_spicy = False

        return next_sliders

    def handle_load_speaker_click(self):
        self.speaker_name_list = self.speaker_service.get_speaker_names()

        return gr.Dropdown(
            choices=self.speaker_name_list,
            visible=True
        )

    def handle_speaker_select_change(self, selected_speakers):
        is_valid_count = len(selected_speakers) > 1

        return [
            gr.Group(visible=is_valid_count),
            gr.Group(visible=is_valid_count)
        ]

    def handle_spicy_click(self):
        self.is_spicy = True
        max_speakers = min(
            len(self.speaker_name_list),
            MAX_SPICY_SPEAKER_COUNT
        )
        speaker_select_count = randrange(2, max_speakers + 1)
        speakers = random.sample(self.speaker_name_list, speaker_select_count)

        return gr.Dropdown(value=speakers)

    def handle_speaker_slider_change(self, slider_value, selected_speakers, evt: gr.EventData):
        slider_index = int(evt.target.elem_id)
        slider_speaker = selected_speakers[slider_index]

        self.update_speaker_weights(slider_speaker, slider_value)

    def handle_generate_speech_click(self):
        self.speaker_embedding = self.speaker_service.create_speaker_embedding_from_mix(
            self.speaker_weights)

        return gr.Column(elem_classes=["ui-disabled"])

    def handle_randomize_speaker_weights_click(self, selected_speakers: SpeakerNameList):
        self.randomize_speaker_weights()

        active_slider_props = {
            "visible": True,
            "value": 1
        }

        inactive_slider_props = {
            "visible": False,
            "value": 0
        }

        return self.update_slider_props(
            selected_speakers,
            active_slider_props,
            inactive_slider_props,
            valueFn=self.get_speaker_weight
        )

    def handle_reset_speaker_weights_click(self, selected_speakers: SpeakerNameList):
        active_slider_props = {
            "visible": True,
            "value": 1
        }

        inactive_slider_props = {
            "visible": False,
            "value": 0
        }

        return self.update_slider_props(
            selected_speakers,
            active_slider_props,
            inactive_slider_props
        )

    def handle_save_speaker_click(self, speaker_name):
        gpt_cond_latent = self.speaker_embedding["gpt_cond_latent"]
        speaker_embedding = self.speaker_embedding["speaker_embedding"]

        self.speaker_service.add_speaker(
            speaker_name=speaker_name,
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding
        )

        self.speaker_service.save_speaker_file()

        return gr.Markdown(
            value=format_notification(
                f"Speaker \"{speaker_name}\" added successfully!")
        )

    def do_inference(self, speech_input_text, language="en"):
        wav_file = None
        gpt_cond_latent = self.speaker_embedding.get("gpt_cond_latent", None)
        speaker_embedding = self.speaker_embedding.get(
            "speaker_embedding", None)

        if speaker_embedding is not None and gpt_cond_latent is not None:
            wav_file = self.model_service.run_inference(
                lang=language,
                tts_text=speech_input_text,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                file_name=self.speaker_weights_to_file_name()
            )
        else:
            print("Speaker embeddings are not set")

        return [
            gr.Button(interactive=True),
            gr.Audio(value=wav_file),
            gr.Column(elem_classes=[]),
            gr.Group(visible=True)
        ]

    def disable_control_list(self, selected_speakers: SpeakerNameList):
        active_slider_props = {
            "interactive": False
        }

        inactive_slider_props = {
            "visible": False,
            "value": 0
        }

        return self.update_slider_props(
            selected_speakers,
            active_slider_props,
            inactive_slider_props
        )

    def enable_control_list(self, selected_speakers: SpeakerNameList):
        active_slider_props = {
            "interactive": True
        }

        inactive_slider_props = {
            "visible": False,
            "value": 0
        }

        return self.update_slider_props(
            selected_speakers,
            active_slider_props,
            inactive_slider_props
        )

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

    def update_slider_props(
        self,
        selected_speakers: SpeakerNameList,
        active_slider_props: dict,
        inactive_slider_props: dict,
        valueFn=None
    ):
        next_slider_list: SliderList = []

        for idx, speaker_control in enumerate(self.speaker_control_list):
            if idx < len(selected_speakers):
                speaker_name = selected_speakers[idx]

                if valueFn:
                    value = valueFn(speaker_name)
                    active_slider_props["value"] = value

                slider = gr.Slider(
                    label=speaker_name,
                    **active_slider_props,
                )
            else:
                slider = gr.Slider(
                    label=UNASSIGNED,
                    **inactive_slider_props
                )

            next_slider_list.append(slider)

        return next_slider_list
