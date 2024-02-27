import os
import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from content_handler import ContentHandler

from forge_base_view import ForgeBaseView
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler
from utils.utils import format_notification, load_changelog_md, load_readme_md


class ForgeAboutView(ForgeBaseView):
    section_content: dict

    def __init__(
        self,
        speaker_handler: SpeakersHandler,
        model_handler: ModelHandler,
        content_handler: ContentHandler
    ):
        super().__init__(speaker_handler, model_handler, content_handler)
        self.section_content = self.content_handler.get_section_content(
            'about')

    def init_ui(self):
        section_description = SectionDescriptionComponent(
            value=self.section_content['section_description'],)

        gr.Markdown(value=self.load_readme(),
                    elem_classes=["about-content"])

    def load_readme(self):
        readme = load_readme_md()

        if readme:
            return readme
        else:
            return format_notification("Ah Shucks! About content not found")
