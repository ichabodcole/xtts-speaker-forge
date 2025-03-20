import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from services.content_manager_service import ContentManagerService
from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from components.speaker_preview_component import SpeechPreviewComponent
from services.speaker_manager_service import SpeakerManagerService
from components.notification_component import NotificationComponent
from utils.utils import format_notification


class ForgeExploreView(ForgeBaseView):
    speaker_data = None
    section_content: dict
    common_content: dict
    speaker_select = None
    current_audio_file = None

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
        
        # Add save sample button in its own group
        with gr.Group(visible=True) as save_sample_group:
            with gr.Row():
                save_sample_btn = gr.Button(
                    self.common_content.get('save_sample_btn_label'),
                    interactive=False  # Start disabled until audio is generated
                )
        
        # Notification area outside of groups for cleaner appearance
        sample_notification = NotificationComponent()

        # Setup the button click events
        self.speaker_select.change(
            self.handle_speaker_select_change,
            inputs=[self.speaker_select],
            outputs=[
                audio_player,
                speech_input_textbox,
                language_select,
                sample_notification,
                save_sample_btn  # Add save button to outputs to disable it
            ]
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
                audio_player,
                sample_notification,
                save_sample_btn  # Add save button to outputs to enable it
            ]
        )
        
        save_sample_btn.click(
            self.save_speaker_sample,
            inputs=[
                self.speaker_select,
                speech_input_textbox,
                language_select
            ],
            outputs=[sample_notification]
        )

    def handle_speaker_select_change(self, speaker):
        """Handle speaker selection - load sample if available"""
        if not speaker:
            return [
                self.reset_audio_player(),
                gr.update(),    # Keep existing speech text
                gr.update(),    # Keep existing language
                gr.Markdown(visible=False),
                gr.Button(interactive=False)  # Disable save button
            ]
            
        # Try to load speaker sample
        sample_data = self.speaker_service.get_speaker_sample(speaker)
        
        if sample_data:
            # We have a sample, load it
            return [
                gr.Audio(value=sample_data["audio_path"], format="wav"),
                sample_data["text"],
                sample_data["language"],
                gr.Markdown(
                    value=format_notification(
                        self.common_content.get('sample_loaded_msg')
                    ),
                    visible=True
                ),
                gr.Button(interactive=False)  # Disable save button for loaded samples
            ]
        
        # No sample, reset just the audio player but keep existing text
        return [
            self.reset_audio_player(),
            gr.update(),    # Keep existing speech text
            gr.update(),    # Keep existing language
            gr.Markdown(visible=False),
            gr.Button(interactive=False)  # Disable save button
        ]

    def do_inference(self, speaker, speech_text, language="en"):
        self.speaker_data = self.speaker_service.get_speaker_data(speaker)
        self.current_audio_file = None

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
            self.current_audio_file = wav_file

        # Determine if save button should be enabled
        save_button_interactive = wav_file is not None

        return [
            gr.Dropdown(interactive=True),
            gr.Button(interactive=True),
            gr.Audio(value=wav_file, format="wav"),
            gr.Markdown(visible=False),
            gr.Button(interactive=save_button_interactive)  # Enable save button only if audio was generated
        ]
        
    def save_speaker_sample(self, speaker, speech_text, language):
        """Save the current sample to the speaker's metadata"""
        if not self.current_audio_file or not speaker:
            return gr.Markdown(
                value=format_notification(
                    "⚠️ " + self.common_content.get('save_sample_failure_msg')
                ),
                visible=True
            )
            
        success = self.speaker_service.save_speaker_sample(
            speaker_name=speaker,
            sample_text=speech_text,
            audio_path=self.current_audio_file,
            language=language
        )
        
        if success:
            # Also save the speaker file
            self.speaker_service.save_speaker_file()
            return gr.Markdown(
                value=format_notification(
                    self.common_content.get('save_sample_success_msg')
                ),
                visible=True
            )
        else:
            return gr.Markdown(
                value=format_notification(
                    "⚠️ Failed to save sample"
                ),
                visible=True
            )

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
