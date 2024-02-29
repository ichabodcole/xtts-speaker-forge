import gradio as gr
from components.notification_component import NotificationComponent
from components.section_description_component import SectionDescriptionComponent
from services.content_manager_service import ContentManagerService
from types_module import SpeakerFileData
from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService
from utils.utils import format_notification


class ForgeImportView(ForgeBaseView):
    section_content: dict
    common_content: dict
    to_speakers: list[str] = []
    from_speaker_data: SpeakerFileData = None

    def __init__(
        self,
        speakers_handler: SpeakerManagerService,
        model_service: ModelManagerService,
        content_service: ContentManagerService
    ):
        super().__init__(speakers_handler, model_service, content_service)
        self.section_content = self.content_service.get_section_content(
            'import')
        self.common_content = self.content_service.get_common_content()

    def init_ui(self):
        section_description = SectionDescriptionComponent(
            value=self.section_content.get('section_description')
        )

        with gr.Column() as ui_container:
            load_speakers_btn = gr.Button(
                self.common_content.get('load_speakers_btn_label'))

            with gr.Row(visible=False) as speaker_lists_group:
                with gr.Group():
                    speakers_to_list = gr.Markdown(
                        label="To Speaker List",
                        value=None,
                        elem_classes=["import-speaker-to-list"]
                    )

                with gr.Group():
                    speaker_from_checkbox_group = gr.CheckboxGroup(
                        label="From Speaker List",
                        info="Speakers will be imported from this speaker list.",
                        interactive=True,
                        visible=False
                    )

                    with gr.Group(visible=False) as speaker_from_actions_group:
                        with gr.Row():
                            select_all_btn = gr.Button("Select All")
                            deselect_all_btn = gr.Button("Deselect All")

                        load_new_speaker_file_btn = gr.Button(
                            "Load New Speaker File")

                    file_uploader = gr.File(
                        label="Import Speaker File",
                        file_types=['.pth'],
                        interactive=True)

            import_speakers_btn = gr.Button(
                "Import Speakers",
                visible=False,
                interactive=False
            )

        # Setup Event Handlers
        load_speakers_btn.click(
            self.load_speaker_data,
            outputs=speakers_to_list
        ).then(
            lambda: [
                gr.Group(visible=True),
                gr.Button(visible=True)
            ],
            outputs=[
                speaker_lists_group,
                import_speakers_btn
            ]
        )

        file_uploader.change(
            self.file_uploader_change,
            inputs=file_uploader,
            outputs=speaker_from_checkbox_group
        ).then(
            lambda: [
                gr.File(value=None, visible=False),
                gr.Group(visible=True)
            ],
            outputs=[
                file_uploader,
                speaker_from_actions_group
            ]
        )

        speaker_from_checkbox_group.change(
            lambda selected_speakers: gr.Button(
                interactive=len(selected_speakers) > 0
            ),
            inputs=speaker_from_checkbox_group,
            outputs=import_speakers_btn
        )

        select_all_btn.click(
            lambda: gr.CheckboxGroup(
                value=self.get_speaker_names_from_data(self.from_speaker_data)),
            outputs=speaker_from_checkbox_group
        )

        deselect_all_btn.click(
            lambda: gr.CheckboxGroup(value=[]),
            outputs=speaker_from_checkbox_group
        )

        load_new_speaker_file_btn.click(
            lambda: [
                gr.CheckboxGroup(visible=False, choices=[], value=[]),
                gr.File(visible=True),
                gr.Group(visible=False)
            ],
            outputs=[
                speaker_from_checkbox_group,
                file_uploader,
                speaker_from_actions_group
            ]
        )

        import_speakers_btn.click(
            self.import_speakers,
            inputs=speaker_from_checkbox_group,
            outputs=speakers_to_list
        )

    def file_uploader_change(self, file):
        if file:
            self.from_speaker_data = self.speakers_handler.import_speakers_from_file(
                file)

            speaker_names = self.get_speaker_names_from_data(
                self.from_speaker_data)

            return gr.CheckboxGroup(
                choices=speaker_names,
                value=speaker_names,
                visible=True
            )

        return gr.CheckboxGroup()

    def load_speaker_data(self):
        speaker_text = "### Current Speakers\n\n"

        self.to_speakers = self.speakers_handler.get_speaker_names()

        for speaker in self.to_speakers:
            speaker_text += f"  - {speaker}\n"

        return speaker_text

    def import_speakers(self, from_selected_speaker: list[str] | None):
        for speaker in from_selected_speaker:
            speaker_data = self.from_speaker_data.get(speaker)

            if speaker_data is not None:
                self.speakers_handler.add_speaker(
                    speaker,
                    speaker_data.get("gpt_cond_latent"),
                    speaker_data.get("speaker_embedding"),
                    speaker_data.get("metadata", None)
                )

        self.speakers_handler.save_speaker_file()

        return self.load_speaker_data()

    def get_speaker_names_from_data(self, speaker_data: SpeakerFileData):
        return list(speaker_data.keys())
