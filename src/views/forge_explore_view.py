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

        load_speakers_btn = gr.Button(
            self.common_content.get('load_speakers_btn_label'))

        with gr.Group(visible=False) as speaker_group:
            with gr.Row():
                speaker_select = gr.Dropdown(
                    label=self.common_content.get(
                        'select_speaker_dropdown_label'),
                    choices=[],
                    scale=3
                )

        (audio_preview_group,
         audio_player,
         speech_input_textbox,
         language_select,
         generate_speech_btn) = SpeechPreviewComponent(self.content_service.get_common_content())

        # Setup the button click events
        speaker_select.change(
            self.reset_audio_player,
            inputs=[],
            outputs=[audio_player]
        )

        load_speakers_btn.click(
            self.load_speaker_data,
            inputs=[],
            outputs=speaker_select
        ).then(
            lambda: [gr.Group(visible=True), gr.Group(visible=True)],
            outputs=[speaker_group, audio_preview_group]
        )

        generate_speech_btn.click(
            lambda: gr.Dropdown(interactive=False),
            outputs=speaker_select
        ).then(
            self.do_inference,
            inputs=[
                speaker_select,
                speech_input_textbox,
                language_select
            ],
            outputs=[
                speaker_select,
                generate_speech_btn,
                audio_player
            ]
        )

    def load_speaker_data(self):
        speakers = self.speaker_service.get_speaker_names()

        return gr.Dropdown(
            choices=speakers,
            visible=True,
            value=speakers[0],
            interactive=True
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
            gr.Audio(value=wav_file)
        ]

    def reset_audio_player(self):
        return gr.Audio(value=None)
