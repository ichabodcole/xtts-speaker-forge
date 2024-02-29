import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from components.textbox_submit_component import TextboxSubmitComponent
from services.content_manager_service import ContentManagerService
from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService


class ForgeExportView(ForgeBaseView):
    section_content: dict

    def __init__(
        self,
        speaker_handler: SpeakerManagerService,
        model_handler: ModelManagerService,
        content_handler: ContentManagerService
    ):
        super().__init__(speaker_handler, model_handler, content_handler)
        self.section_content = self.content_handler.get_section_content(
            'export')
        self.common_content = self.content_handler.get_common_content()

    def init_ui(self):
        section_description = SectionDescriptionComponent(
            value=self.section_content.get('section_description'))

        load_speakers_btn = gr.Button(
            self.common_content.get('load_speakers_btn_label'))

        with gr.Group(visible=False) as speaker_transfer_group:
            gr.Label(self.section_content.get('speaker_checkbox_group_label'))

            speaker_checkbox_group = gr.CheckboxGroup(
                label=None,
                choices=self.speakers_handler.get_speaker_names(),
                value=self.speakers_handler.get_speaker_names(),
                interactive=True
            )

            with gr.Row():
                select_all_btn = gr.Button(
                    self.section_content.get('select_all_btn_label'))

                deselect_all_btn = gr.Button(
                    self.section_content.get('deselect_all_btn_label'))

        export_file_btn = gr.Button(
            value=self.section_content.get('export_file_btn_label'),
            visible=False
        )

        download_file = gr.File(
            label=self.section_content.get("download_file_label"),
            visible=False
        )

        load_speakers_btn.click(
            self.load_speakers,
            outputs=[speaker_checkbox_group]
        ).then(
            lambda: [gr.Group(visible=True), gr.Button(visible=True)],
            outputs=[speaker_transfer_group, export_file_btn]
        )

        select_all_btn.click(
            lambda: gr.CheckboxGroup(
                choices=self.speakers_handler.get_speaker_names(),
                value=self.speakers_handler.get_speaker_names()
            ),
            outputs=[speaker_checkbox_group]
        )

        deselect_all_btn.click(
            lambda: gr.CheckboxGroup(
                choices=self.speakers_handler.get_speaker_names(),
                value=[]
            ),
            outputs=[speaker_checkbox_group]
        )

        export_file_btn.click(
            self.export_speaker_file,
            inputs=[speaker_checkbox_group],
            outputs=[download_file]
        )

        gr.on(
            triggers=[
                speaker_checkbox_group.change,
                export_file_btn.click,
                load_speakers_btn.click
            ],
            fn=lambda: gr.File(value=None, visible=False),
            outputs=[download_file]
        )

    def load_speakers(self):
        speaker_names = self.speakers_handler.get_speaker_names()

        return gr.CheckboxGroup(
            choices=speaker_names,
            value=speaker_names
        )

    def export_speaker_file(self, selected_speakers):
        file_path = self.speakers_handler.create_speaker_file_from_selected_speakers(
            selected_speakers)

        return gr.File(value=file_path, visible=True)
