import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from components.textbox_submit_component import TextboxSubmitComponent
from services.content_manager_service import ContentManagerService
from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService


class ForgeExportView(ForgeBaseView):
    section_content: dict
    speaker_checkbox_group = None

    def __init__(
        self,
        speaker_service: SpeakerManagerService,
        model_service: ModelManagerService,
        content_service: ContentManagerService
    ):
        super().__init__(speaker_service, model_service, content_service)
        self.section_content = self.content_service.get_section_content(
            'export')
        self.common_content = self.content_service.get_common_content()

    def init_ui(self):
        section_description = SectionDescriptionComponent(
            value=self.section_content.get('section_description'))

        # Speaker selection group - now visible by default
        with gr.Group(visible=True) as self.speaker_transfer_group:
            gr.Label(value=self.section_content.get('speaker_checkbox_group_label'))

            # Create a multi-column layout for the checkbox group
            with gr.Row() as speaker_list_row:
                with gr.Column(scale=1, min_width=200):
                    self.speaker_checkbox_group = gr.CheckboxGroup(
                        label=None,
                        choices=self.speaker_service.get_speaker_names(),
                        value=self.speaker_service.get_speaker_names(),
                        interactive=True,
                        elem_classes=["speaker-checkbox-grid"]
                    )

            with gr.Row():
                select_all_btn = gr.Button(
                    value=self.section_content.get('select_all_btn_label'))

                deselect_all_btn = gr.Button(
                    value=self.section_content.get('deselect_all_btn_label'))

        export_file_btn = gr.Button(
            value=self.section_content.get('export_file_btn_label'),
            visible=True
        )

        download_file = gr.File(
            label=self.section_content.get("download_file_label"),
            visible=False
        )

        select_all_btn.click(
            lambda: gr.CheckboxGroup(
                choices=self.speaker_service.get_speaker_names(),
                value=self.speaker_service.get_speaker_names()
            ),
            outputs=[self.speaker_checkbox_group]
        )

        deselect_all_btn.click(
            lambda: gr.CheckboxGroup(
                choices=self.speaker_service.get_speaker_names(),
                value=[]
            ),
            outputs=[self.speaker_checkbox_group]
        )

        export_file_btn.click(
            self.export_speaker_file,
            inputs=[self.speaker_checkbox_group],
            outputs=[download_file]
        )

        gr.on(
            triggers=[
                self.speaker_checkbox_group.change,
                export_file_btn.click
            ],
            fn=lambda: gr.File(value=None, visible=False),
            outputs=[download_file]
        )

    def export_speaker_file(self, selected_speakers):
        file_path = self.speaker_service.create_speaker_file_from_selected_speakers(
            selected_speakers)

        return gr.File(value=file_path, visible=True)
    
    def reload_speaker_data(self, *args):
        """
        Override the base reload method to update the UI with fresh speaker data
        Accepts *args to handle any arguments Gradio might pass
        """
        # First reload the data using the parent method
        super().reload_speaker_data()
        
        # If we have a checkbox group component initialized and data was reloaded
        if self.speaker_checkbox_group is not None:
            # Get fresh speaker names and update the checkbox component
            speaker_names = self.speaker_service.get_speaker_names()
            
            # This will update the UI on the next render
            return gr.update(
                choices=speaker_names,
                value=speaker_names
            )
        
        return None
