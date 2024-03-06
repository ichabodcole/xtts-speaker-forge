import os
import shutil
import tempfile
import gradio as gr
from components.notification_component import NotificationComponent
from components.section_description_component import SectionDescriptionComponent
from services.content_manager_service import ContentManagerService
from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService
from utils.utils import format_notification


class ForgeSetupView(ForgeBaseView):
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
            'setup')
        self.common_content = self.content_service.get_common_content()

    def set_tabs(self, explore_tab: gr.Tab, create_tab: gr.Tab, mix_tab: gr.Tab, edit_tab: gr.Tab, import_tab: gr.Tab, export_tab: gr.Tab):
        self.explore_tab = explore_tab
        self.create_tab = create_tab
        self.mix_tab = mix_tab
        self.edit_tab = edit_tab
        self.import_tab = import_tab
        self.export_tab = export_tab
        self.is_tabs_set = True

    def set_file_paths(self, checkpoint_dir, vocab_file, config_file, speaker_file):
        self.checkpoint_dir = checkpoint_dir
        self.vocab_file = vocab_file
        self.config_file = config_file
        self.speaker_file = speaker_file
        self.is_file_paths_set = True

    def init_ui(self):
        if not self.is_tabs_set:
            raise ValueError(
                "Tabs not set. Call add_tabs method before creating UI")
        if not self.is_file_paths_set:
            raise ValueError(
                "File paths not set. Call add_file_paths method before creating UI")

        section_description = SectionDescriptionComponent(
            value=self.section_content.get('section_description')
        )

        with gr.Column() as ui_container:
            checkpoint_dir_textbox = gr.Textbox(
                value=self.checkpoint_dir,
                label=self.section_content.get('checkpoint_dir_label'),
                interactive=False,
                max_lines=1
            )
            vocab_file_textbox = gr.Textbox(
                value=self.vocab_file,
                label=self.section_content.get('vocab_file_label'),
                interactive=False,
                max_lines=1
            )
            config_file_textbox = gr.Textbox(
                value=self.config_file,
                label=self.section_content.get('config_file_label'),
                interactive=False,
                max_lines=1
            )
            speaker_file_textbox = gr.Textbox(
                value=self.speaker_file,
                label=self.section_content.get('speaker_file_label'),
                interactive=False,
                max_lines=1
            )

            load_model_btn = gr.Button(
                value=self.section_content.get("load_model_btn_label"))

            result_message = NotificationComponent(
                label="Result", value=self.section_content.get("model_load_start"))

            load_model_btn.click(
                lambda: [gr.Button(interactive=False),
                         gr.Markdown(visible=True)],
                inputs=[],
                outputs=[load_model_btn, result_message]
            ).then(
                self.validate_paths_and_load_model,
                inputs=[
                    checkpoint_dir_textbox,
                    vocab_file_textbox,
                    config_file_textbox,
                    speaker_file_textbox
                ],
                outputs=[
                    load_model_btn,
                    result_message,
                    self.explore_tab,
                    self.create_tab,
                    self.mix_tab,
                    self.edit_tab,
                    self.import_tab,
                    self.export_tab,
                ]
            )

    def validate_paths_and_load_model(self, checkpoint_dir, vocab_file, config_file, speaker_file):

        def response(message, is_ui_enabled):
            return [
                gr.Button(interactive=is_ui_enabled),
                gr.Markdown(value=message),
                gr.Tab(interactive=is_ui_enabled),
                gr.Tab(interactive=is_ui_enabled),
                gr.Tab(interactive=is_ui_enabled),
                gr.Tab(interactive=is_ui_enabled),
                gr.Tab(interactive=is_ui_enabled),
                gr.Tab(interactive=is_ui_enabled)
            ]

        try:
            if (self.speaker_service.get_speaker_file() is None):
                temp_file_path = self.create_temp_speaker_file(speaker_file)
                self.speaker_service.set_speaker_file(temp_file_path)

        except Exception as e:
            md_message = format_notification(
                self.section_content.get("speaker_file_error"))
            is_ui_enabled = False

            return response(md_message, is_ui_enabled)

        try:
            self.model_service.set_file_paths(
                checkpoint_dir,
                vocab_file,
                config_file
            )
        except Exception as e:
            md_message = format_notification(
                self.section_content.get("model_file_paths_invalid"))
            is_ui_enabled = False
            return response(md_message, is_ui_enabled)

        try:
            self.model_service.load_model()
            md_message = format_notification(
                self.section_content.get("model_load_success"))
            is_ui_enabled = True
            return response(md_message, is_ui_enabled)

        except Exception as e:
            md_message = format_notification(f"Error: {e}")
            is_ui_enabled = False
            return response(md_message, is_ui_enabled)

    def create_temp_speaker_file(self, speaker_file):
        if os.path.exists(speaker_file):
            with tempfile.NamedTemporaryFile(suffix=".pth", delete=False) as temp_file:
                temp_file_name = temp_file.name

                file_path = shutil.copy(speaker_file, temp_file_name)

            return file_path

        print("Speaker file does not exist")
        return None
