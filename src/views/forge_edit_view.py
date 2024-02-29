import gradio as gr
from components.notification_component import NotificationComponent
from components.section_description_component import SectionDescriptionComponent
from constants.common import ACCENT_CHOICES, AGE_RANGE_CHOICES, CHARACTER_TYPE_CHOICES, GENDER_CHOICES, GENRE_CHOICES, STYLE_CHOICES, TONAL_CHOICES
from services.content_manager_service import ContentManagerService
from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService
from types_module import SpeakerMetadata
from utils.utils import is_empty_string


class ForgeEditView(ForgeBaseView):
    is_tabs_set = False
    is_file_paths_set = False
    section_content: dict
    common_content: dict

    def __init__(
        self,
        speaker_service: SpeakerManagerService,
        model_service: ModelManagerService,
        content_service: ContentManagerService
    ):
        super().__init__(speaker_service, model_service, content_service)
        self.section_content = self.content_service.get_section_content(
            'edit')
        self.common_content = self.content_service.get_common_content()

    def init_ui(self):
        section_description = SectionDescriptionComponent(
            value=self.section_content.get('section_description'))

        load_speakers_btn = gr.Button(
            self.common_content.get('load_speakers_btn_label'))

        with gr.Column() as ui_container:
            with gr.Group(visible=False) as speaker_select_group:
                with gr.Row():
                    speaker_select = gr.Dropdown(
                        label=self.common_content.get(
                            'select_speaker_dropdown_label'
                        ),
                        choices=[],
                        interactive=True,
                        scale=3
                    )

                    speaker_remove_btn = gr.Button(
                        self.section_content.get('remove_speaker_btn_label'),
                        visible=False,
                        scale=1
                    )

            with gr.Group(visible=False) as speaker_edit_group:
                speaker_edit_label = gr.Label(
                    self.section_content.get('edit_speaker_group_label'))

                with gr.Row():
                    speaker_name_input = gr.Textbox(label=self.section_content.get(
                        'speaker_name_input_label'), interactive=True)

                    speaker_gender_input = gr.Dropdown(
                        label=self.section_content.get('gender_input_label'),
                        choices=GENDER_CHOICES,
                        interactive=True
                    )

                with gr.Row():
                    speaker_age_range_input = gr.Dropdown(
                        label=self.section_content.get(
                            'age_range_input_label'),
                        choices=AGE_RANGE_CHOICES,
                        interactive=True
                    )

                    speaker_accent_input = gr.Dropdown(
                        label=self.section_content.get('accent_input_label'),
                        choices=ACCENT_CHOICES,
                        interactive=True
                    )

                with gr.Row():
                    speaker_tonal_quality_input = gr.Dropdown(
                        label=self.section_content.get(
                            'tonal_quality_input_label'),
                        choices=TONAL_CHOICES,
                        multiselect=True,
                        interactive=True
                    )

                    speaker_style_input = gr.Dropdown(
                        label=self.section_content.get('style_input_label'),
                        choices=STYLE_CHOICES,
                        multiselect=True,
                        interactive=True
                    )

                with gr.Row():
                    speaker_genre_input = gr.Dropdown(
                        label=self.section_content.get('genre_input_label'),
                        choices=GENRE_CHOICES,
                        multiselect=True,
                        interactive=True
                    )

                    speaker_character_type_input = gr.Dropdown(
                        label=self.section_content.get(
                            'character_type_input_label'),
                        choices=CHARACTER_TYPE_CHOICES,
                        multiselect=True,
                        interactive=True
                    )

                speaker_description_input = gr.Textbox(
                    label=self.section_content.get('description_input_label'),
                    placeholder=self.section_content.get(
                        'description_input_placeholder'),
                    lines=3,
                    interactive=True
                )

                speaker_save_changes_btn = gr.Button(self.section_content.get(
                    'save_changes_btn_label'), interactive=False)

            notification_message = NotificationComponent()

        load_speakers_btn.click(
            self.load_speaker_data,
            inputs=[speaker_select],
            outputs=speaker_select
        ).then(
            lambda: [
                gr.Group(visible=True),
                gr.Button(visible=True)
            ],
            outputs=[
                speaker_select_group,
                speaker_remove_btn
            ]
        )

        speaker_select.change(
            self.update_speaker_fields,
            inputs=[speaker_select],
            outputs=[
                speaker_edit_group,
                speaker_edit_label,
                speaker_name_input,
                speaker_gender_input,
                speaker_age_range_input,
                speaker_accent_input,
                speaker_tonal_quality_input,
                speaker_style_input,
                speaker_genre_input,
                speaker_character_type_input,
                speaker_description_input
            ]
        ).then(
            lambda: gr.Markdown(visible=False),
            outputs=notification_message
        )

        speaker_name_input.change(
            lambda speaker_name: gr.Button(interactive=False) if is_empty_string(
                speaker_name) else gr.Button(interactive=True),
            inputs=[speaker_name_input],
            outputs=speaker_save_changes_btn
        )

        speaker_save_changes_btn.click(
            self.save_speaker_changes,
            inputs=[
                speaker_select,
                speaker_name_input,
                speaker_gender_input,
                speaker_age_range_input,
                speaker_accent_input,
                speaker_tonal_quality_input,
                speaker_style_input,
                speaker_genre_input,
                speaker_character_type_input,
                speaker_description_input,
            ],
            outputs=notification_message
        ).then(
            self.load_speaker_data,
            inputs=[speaker_select],
            outputs=speaker_select
        )

        speaker_remove_btn.click(
            self.remove_speaker,
            inputs=[speaker_select],
            outputs=notification_message
        ).then(
            self.load_speaker_data,
            inputs=[speaker_select],
            outputs=speaker_select
        )

    # Event Handlers
    def load_speaker_data(self, selected_speaker=None):
        speakers = self.speakers_handler.get_speaker_names()

        speaker = selected_speaker if selected_speaker in speakers else speakers[0]

        return gr.Dropdown(
            choices=speakers,
            visible=True,
            value=speaker
        )

    def update_speaker_fields(self, selected_speaker):

        speaker_metadata = self.speakers_handler.get_speaker_metadata(
            selected_speaker) or {}

        name = selected_speaker
        description = speaker_metadata.get('description', None)
        age_range = speaker_metadata.get('age_range', None)
        gender = speaker_metadata.get('gender', None)
        accent = speaker_metadata.get('accent', None)
        tonal_quality = speaker_metadata.get('tonal_quality', [])
        style = speaker_metadata.get('style', [])
        genre = speaker_metadata.get('genre', [])
        character_type = speaker_metadata.get('character_type', [])

        return [
            # speaker_edit_group,
            gr.Group(visible=True),
            # speaker_edit_label,
            gr.Label(value=f"Attributes for {selected_speaker}"),
            # speaker_name_input,
            gr.Textbox(value=name),
            # speaker_gender_input,
            gr.Dropdown(value=gender),
            # speaker_age_range_input,
            gr.Dropdown(value=age_range),
            # speaker_accent_input,
            gr.Dropdown(value=accent),
            # speaker_tonal_quality_input,
            gr.Dropdown(value=tonal_quality),
            # speaker_style_input,
            gr.Dropdown(value=style),
            # speaker_genre_input,
            gr.Dropdown(value=genre),
            # speaker_character_type_input,
            gr.Dropdown(value=character_type),
            # speaker_description_input
            gr.Textbox(value=description)
        ]

    def remove_speaker(self, selected_speaker):
        self.speakers_handler.remove_speaker(selected_speaker)
        self.speakers_handler.save_speaker_file()

        return gr.Markdown(value=f"Speaker {selected_speaker} Removed!", visible=True)

    def save_speaker_changes(
        self,
        selected_speaker,
        speaker_name,
        speaker_gender,
        speaker_age_range,
        speaker_accent,
        speaker_tonal_quality,
        speaker_style,
        speaker_genre,
        speaker_character_type,
        speaker_description
    ):
        if speaker_name is None or str(speaker_name).strip() == "":
            return gr.Markdown("Speaker Name is required", visible=True)

        speaker_metadata: SpeakerMetadata = {
            "speaker_name": speaker_name,
            "gender": speaker_gender,
            "age_range": speaker_age_range,
            "accent": speaker_accent,
            "tonal_quality": speaker_tonal_quality,
            "style": speaker_style,
            "genre": speaker_genre,
            "character_type": speaker_character_type,
            "description": speaker_description
        }

        self.speakers_handler.update_speaker_meta(
            selected_speaker, speaker_metadata)

        self.speakers_handler.save_speaker_file()

        return gr.Markdown(value=f"Speaker {selected_speaker} Attributes Update!", visible=True)
