import os
import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from services.content_handler import ContentHandler

from views.forge_base_view import ForgeBaseView
from services.model_handler import ModelHandler
from services.speakers_handler import SpeakersHandler
from utils.utils import format_notification, load_changelog_md


class ForgeChangelogView(ForgeBaseView):
    section_content: dict

    def __init__(
        self,
        speaker_handler: SpeakersHandler,
        model_handler: ModelHandler,
        content_handler: ContentHandler
    ):
        super().__init__(speaker_handler, model_handler, content_handler)
        self.section_content = self.content_handler.get_section_content(
            'changelog')

    def init_ui(self):
        section_description = SectionDescriptionComponent(
            value=self.section_content['section_description'])

        gr.Markdown(value=self.load_changelog(),
                    elem_classes=["changelog-content"])

    def load_changelog(self):
        changelog = load_changelog_md()

        if changelog:
            return changelog
        else:
            return format_notification("Ah Shucks! Changelog file not found")
