import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from services.content_manager_service import ContentManagerService
from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from components.speaker_preview_component import SpeechPreviewComponent
from services.speaker_manager_service import SpeakerManagerService


class ForgeExploreView(ForgeBaseView):
    speaker_data = None
    section_content: dict
    common_content: dict
    speaker_select = None

    def __init__(
        self,
        speaker_service: SpeakerManagerService,
        model_service: ModelManagerService,
        content_service: ContentManagerService
    ):
        super().__init__(speaker_service, model_service, content_service)
        self.section_content = self.content_service.get_section_content(
            'explore')
        self.common_content = self.content_service.get_common_content()

    def init_ui(self):
        section_description = SectionDescriptionComponent(
            value=self.section_content.get('section_description'))

        # Make speaker group visible by default
        with gr.Group(visible=True) as speaker_group:
            with gr.Row():
                self.speaker_select = gr.Dropdown(
                    label=self.common_content.get(
                        'select_speaker_dropdown_label'),
                    choices=[],  # Start with empty list, will be populated on tab select
                    value=None,  # No default value initially
                    scale=3,
                    interactive=True
                )

        (audio_preview_group,
         audio_player,
         speech_input_textbox,
         language_select,
         generate_speech_btn) = SpeechPreviewComponent(self.content_service.get_common_content())

        # Make the audio controls visible by default
        audio_preview_group.visible = True

        # Setup the button click events
        self.speaker_select.change(
            self.reset_audio_player,
            inputs=[],
            outputs=[audio_player]
        )

        generate_speech_btn.click(
            lambda: gr.Dropdown(interactive=False),
            outputs=self.speaker_select
        ).then(
            self.do_inference,
            inputs=[
                self.speaker_select,
                speech_input_textbox,
                language_select
            ],
            outputs=[
                self.speaker_select,
                generate_speech_btn,
                audio_player
            ]
        )

    def do_inference(self, speaker, speech_text, language="en"):
        self.speaker_data = self.speaker_service.get_speaker_data(speaker)

        wav_file = None

        if self.speaker_data:
            gpt_cond_latent = self.speaker_data['gpt_cond_latent']
            speaker_embedding = self.speaker_data['speaker_embedding']

            wav_file = self.model_service.run_inference(
                lang=language,
                tts_text=speech_text,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding
            )

        return [
            gr.Dropdown(interactive=True),
            gr.Button(interactive=True),
            gr.Audio(value=wav_file, format="wav")
        ]

    def reset_audio_player(self):
        return gr.Audio(value=None, format="wav")
        
    def reload_speaker_data(self, *args):
        """
        Override the base reload method to automatically refresh speaker list
        Accepts *args to handle any arguments Gradio might pass
        """
        # First reload the data using the parent method
        super().reload_speaker_data()
        
        # Always update the dropdown with the latest speaker names
        # regardless of whether the parent reload succeeded
        if self.speaker_select is not None:
            speaker_names = self.speaker_service.get_speaker_names()
            default_speaker = speaker_names[0] if speaker_names else None
            
            return gr.update(
                choices=speaker_names,
                value=default_speaker
            )
        
        return None
