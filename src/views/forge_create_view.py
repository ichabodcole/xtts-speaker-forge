import time
import gradio as gr
from components.notification_component import NotificationComponent
from components.section_description_component import SectionDescriptionComponent
from components.speaker_preview_component import SpeechPreviewComponent
from components.textbox_submit_component import TextboxSubmitComponent
from services.content_manager_service import ContentManagerService
from views.forge_base_view import ForgeBaseView
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService
from utils.utils import format_notification, is_empty_file_list


class ForgeCreateView(ForgeBaseView):
    gpt_cond_latent = None
    speaker_embedding = None
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
            "create")
        self.common_content = self.content_service.get_common_content()

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
             preview_speaker_btn) = SpeechPreviewComponent(self.content_service.get_common_content())

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
                lambda file_list: [
                    gr.Button(interactive=(not is_empty_file_list(file_list))),
                    gr.Audio(value=None, format="wav")
                ],
                inputs=[file_uploader],
                outputs=[
                    create_speaker_embedding_btn,
                    speaker_audio_player
                ]
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
        gpt_cond_latent, speaker_embedding = self.model_service.extract_speaker_embedding(
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
            gr.Audio(value=None, format="wav"),
            gr.Markdown(visible=False)
        ]

    def do_inference(self, speech_text, language="en"):
        wav_file = None

        if (self.gpt_cond_latent is not None and self.speaker_embedding is not None):
            wav_file = self.model_service.run_inference(
                lang=language,
                tts_text=speech_text,
                gpt_cond_latent=self.gpt_cond_latent,
                speaker_embedding=self.speaker_embedding
            )
        else:
            print("Speaker embeddings are not set")

        return [
            gr.Button(interactive=True),
            gr.Audio(value=wav_file, format="wav"),
            gr.Group(visible=True)
        ]

    def save_speaker(self, speaker_name):
        if (speaker_name is None):
            return gr.Markdown(
                value=format_notification(
                    "Speaker name is empty! Please enter a unique speaker name."),
                visible=True
            )

        cur_speaker_names = self.speaker_service.get_speaker_names()
        if speaker_name in cur_speaker_names:
            return gr.Markdown(
                value=format_notification(
                    "Speak name already exists! Please enter a unique speaker name."),
                visible=True
            )

        self.speaker_service.add_speaker(
            speaker_name, self.gpt_cond_latent, self.speaker_embedding)

        self.speaker_service.save_speaker_file()

        return gr.Markdown(
            value=format_notification(
                f"Speaker \"{speaker_name}\" added successfully!"),
            visible=True
        )

    def reload_speaker_data(self, *args):
        """
        Override the base reload method to update the UI with fresh speaker data
        Accepts *args to handle any arguments Gradio might pass
        """
        # First reload the data using the parent method
        super().reload_speaker_data()
        
        # For Create view, we don't need to update any UI components directly
        # since it doesn't display existing speakers
        return None
