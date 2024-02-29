import os
import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from services.content_manager_service import ContentManagerService

from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService
from utils.utils import format_notification, load_changelog_md, load_readme_md


class ForgeAboutView(ForgeBaseView):
    section_content: dict

    def __init__(
        self,
        speaker_service: SpeakerManagerService,
        model_service: ModelManagerService,
        content_service: ContentManagerService
    ):
        super().__init__(speaker_service, model_service, content_service)
        self.section_content = self.content_service.get_section_content(
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
