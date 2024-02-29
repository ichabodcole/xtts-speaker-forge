import time
import gradio as gr
from components.notification_component import NotificationComponent
from components.section_description_component import SectionDescriptionComponent
from components.speaker_preview_component import SpeechPreviewComponent
from components.textbox_submit_component import TextboxSubmitComponent
from services.content_handler import ContentHandler
from views.forge_base_view import ForgeBaseView
from services.model_handler import ModelHandler
from services.speakers_handler import SpeakersHandler
from utils.utils import format_notification, get_random_speech_text, is_empty_file_list, is_empty_string


class ForgeCreateView(ForgeBaseView):
    gpt_cond_latent = None
    speaker_embedding = None
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
            "create")
        self.common_content = self.content_handler.get_common_content()

    def init_ui(self):
        section_description = SectionDescriptionComponent(
            value=self.section_content.get("section_description"))

        with gr.Column() as ui_container:
            with gr.Group() as speaker_upload_group:
                file_uploader = gr.File(
                    label=self.section_content.get("file_uploader_label"),
                    type="filepath",
                    file_count="multiple",
                    file_types=["wav", "mp3"],
                    interactive=True
                )

                create_speaker_embedding_btn = gr.Button(
                    value=self.section_content.get(
                        "create_speaker_embedding_btn_label"),
                    interactive=False
                )

            speaker_embedding_text = NotificationComponent(
                value=self.section_content.get("notification_create_embedding"))

            # SPEAKER PREVIEW COMPONENT
            (speaker_preview_group,
             speaker_audio_player,
             speech_textbox,
             language_select,
             preview_speaker_btn) = SpeechPreviewComponent(self.content_handler.get_common_content())

            speech_textbox.change(
                lambda text: gr.Button(interactive=is_empty_string(text)),
                inputs=[speech_textbox],
                outputs=preview_speaker_btn
            )

            # SAVE SPEAKER COMPONENT
            (speaker_save_group,
             speaker_name_textbox,
             save_speaker_btn,
             save_group_messages) = TextboxSubmitComponent(
                textbox_label=self.common_content.get(
                    "save_speaker_name_label"),
                button_label=self.common_content.get("save_speaker_btn_label"),
                placeholder=self.common_content.get(
                    "save_speaker_placeholder"),
                notification_message=self.common_content.get(
                    "save_speaker_success_msg")
            )

            # Setup Events
            file_uploader.change(
                lambda file_list: gr.Button(
                    interactive=is_empty_file_list(file_list)
                ),
                inputs=[file_uploader],
                outputs=create_speaker_embedding_btn
            )

            # Extracts the speaker embedding from the uploaded audio, then displays the audio player group, but hiding the audio player
            create_speaker_embedding_btn.click(
                lambda: ([
                    gr.Markdown(visible=True),
                    gr.Button(interactive=False),
                    gr.Group(visible=False),
                    gr.Group(visible=False),
                    gr.Markdown(visible=False)
                ]),
                outputs=[
                    speaker_embedding_text,
                    create_speaker_embedding_btn,
                    speaker_preview_group,
                    speaker_save_group,
                    save_group_messages
                ],
            ).then(
                self.get_speaker_embedding,
                inputs=[file_uploader],
                outputs=[
                    speaker_embedding_text,
                    speaker_preview_group
                ]
            )

            # Generates the speech from the speaker embedding and the text,
            preview_speaker_btn.click(
                self.generate_speech,
                outputs=[
                    speaker_preview_group,
                    speaker_save_group,
                    speaker_audio_player,
                    save_group_messages
                ]
            ).then(
                self.do_inference,
                inputs=[speech_textbox, language_select],
                outputs=[
                    preview_speaker_btn,
                    speaker_audio_player,
                    speaker_save_group
                ]
            )

            save_speaker_btn.click(
                self.save_speaker,
                inputs=[speaker_name_textbox],
                outputs=save_group_messages
            )

    def get_speaker_embedding(self, wav_files):
        gpt_cond_latent, speaker_embedding = self.model_handler.extract_speaker_embedding(
            wav_files)

        self.gpt_cond_latent = gpt_cond_latent
        self.speaker_embedding = speaker_embedding

        return [
            gr.Markdown(visible=False),
            gr.Group(visible=True),
        ]

    def generate_speech(self):
        return [
            gr.Group(visible=True),
            gr.Group(visible=False),
            gr.Audio(value=None),
            gr.Markdown(visible=False)
        ]

    def do_inference(self, speech_text, language="en"):
        wav_file = None

        if (self.gpt_cond_latent is not None and self.speaker_embedding is not None):
            wav_file = self.model_handler.run_inference(
                lang=language,
                tts_text=speech_text,
                gpt_cond_latent=self.gpt_cond_latent,
                speaker_embedding=self.speaker_embedding
            )
        else:
            print("Speaker embeddings are not set")

        return [
            gr.Button(interactive=True),
            gr.Audio(value=wav_file),
            gr.Group(visible=True)
        ]

    def save_speaker(self, speaker_name):
        if (speaker_name is None):
            return gr.Markdown(
                value=format_notification(
                    "Speaker name is empty! Please enter a unique speaker name."),
                visible=True
            )

        cur_speaker_names = self.speakers_handler.get_speaker_names()
        if speaker_name in cur_speaker_names:
            return gr.Markdown(
                value=format_notification(
                    "Speak name already exists! Please enter a unique speaker name."),
                visible=True
            )

        self.speakers_handler.add_speaker(
            speaker_name, self.gpt_cond_latent, self.speaker_embedding)

        self.speakers_handler.save_speaker_file()

        return gr.Markdown(
            value=format_notification(
                f"Speaker \"{speaker_name}\" added successfully!"),
            visible=True
        )
