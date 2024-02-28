import gradio as gr
from components.section_description_component import SectionDescriptionComponent
from content_handler import ContentHandler
from forge_base_view import ForgeBaseView
from model_handler import ModelHandler
from components.speaker_preview_component import SpeechPreviewComponent
from speakers_handler import SpeakersHandler


class ForgeExploreView(ForgeBaseView):
    speaker_data = None
    section_content: dict
    common_content: dict

    def __init__(
        self,
        speaker_handler: SpeakersHandler,
        model_handler: ModelHandler,
        content_handler: ContentHandler
    ):
        super().__init__(speaker_handler, model_handler, content_handler)
        self.section_content = self.content_handler.get_section_content(
            'explore')
        self.common_content = self.content_handler.get_common_content()

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
         generate_speech_btn) = SpeechPreviewComponent(self.content_handler.get_common_content())

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
                speech_input_textbox
            ],
            outputs=[
                speaker_select,
                generate_speech_btn,
                audio_player
            ]
        )

    def load_speaker_data(self):
        speakers = self.speakers_handler.get_speaker_names()

        return gr.Dropdown(
            choices=speakers,
            visible=True,
            value=speakers[0],
            interactive=True
        )

    def do_inference(self, speaker, speech_text):
        self.speaker_data = self.speakers_handler.get_speaker_data(speaker)

        wav_file = None

        if self.speaker_data:
            gpt_cond_latent = self.speaker_data['gpt_cond_latent']
            speaker_embedding = self.speaker_data['speaker_embedding']

            wav_file = self.model_handler.run_inference(
                "en", speech_text, gpt_cond_latent, speaker_embedding)

        return [
            gr.Dropdown(interactive=True),
            gr.Button(interactive=True),
            gr.Audio(value=wav_file)
        ]

    def reset_audio_player(self):
        return gr.Audio(value=None)
