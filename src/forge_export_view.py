import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from components.textbox_submit_component import TextboxSubmitComponent
from content_handler import ContentHandler

from forge_base_view import ForgeBaseView
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler


class ForgeExportView(ForgeBaseView):
    section_content: dict

    def __init__(
        self,
        speaker_handler: SpeakersHandler,
        model_handler: ModelHandler,
        content_handler: ContentHandler
    ):
        super().__init__(speaker_handler, model_handler, content_handler)
        self.section_content = self.content_handler.get_section_content(
            'export')

    def init_ui(self):
        section_description = SectionDescriptionComponent(
            value=self.section_content['section_description'])

        export_file_btn = gr.Button(
            value=self.section_content['export_file_btn_label'])

        download_file = gr.File(visible=False)

        export_file_btn.click(
            self.export_speaker_file,
            outputs=[download_file]
        )

    def export_speaker_file(self):
        file_path = self.speakers_handler.speakers_file

        return file_path
