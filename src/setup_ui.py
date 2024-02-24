import gradio as gr
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler


class SetupUI:
    explore_tab = None
    create_tab = None
    mix_tab = None
    export_tab = None

    def __init__(self, speaker_handler: SpeakersHandler, model_handler: ModelHandler):
        self.model_handler = model_handler
        self.speaker_handler = speaker_handler

    def createUI(self, checkpoint_dir, vocab_file, config_file, speaker_file):
        gr.Markdown(
            value="_Ensure the XTTS model paths are correctly setup, and the model can be loaded successfully before proceeding (fingers crossed)._",
            elem_classes=["section-description"]
        )

        checkpoint_dir_textbox = gr.Textbox(
            value=checkpoint_dir,
            label="Checkpoint Directory",
            interactive=False,
            max_lines=1
        )
        vocab_file_textbox = gr.Textbox(
            value=vocab_file,
            label="Vocab File Path",
            interactive=False,
            max_lines=1
        )
        config_file_textbox = gr.Textbox(
            value=config_file,
            label="Config File Path",
            interactive=False,
            max_lines=1
        )
        speaker_file_textbox = gr.Textbox(
            value=speaker_file,
            label="Speaker File Path",
            interactive=False,
            max_lines=1
        )

        load_model_btn = gr.Button("Validate Files and Load XTTS model")

        result_message = gr.Markdown(
            value="### _Validating Files and Loading XTTS Model, wish me luck..._",
            elem_classes=["processing-text"],
            label="Result",
            visible=False
        )

        load_model_btn.click(
            lambda: gr.Markdown(visible=True),
            inputs=[],
            outputs=[result_message]
        )

        return {
            "checkpoint_dir": checkpoint_dir_textbox,
            "vocab_file": vocab_file_textbox,
            "config_file": config_file_textbox,
            "speaker_file": speaker_file_textbox,
            "load_btn": load_model_btn,
            "message": result_message
        }

    def set_tabs(self, explore_tab, create_tab, mix_tab, export_tab):
        self.explore_tab = explore_tab
        self.create_tab = create_tab
        self.mix_tab = mix_tab
        self.export_tab = export_tab

    def validate_paths_and_load_model(self, checkpoint_dir, vocab_file, config_file, speaker_file):
        def response(message, is_ui_enabled):
            return [
                gr.Markdown(value=message),
                gr.Tab(interactive=is_ui_enabled),
                gr.Tab(interactive=is_ui_enabled),
                gr.Tab(interactive=is_ui_enabled),
                gr.Tab(interactive=is_ui_enabled)
            ]

        try:
            self.speaker_handler.set_speaker_file(speaker_file)
        except Exception as e:
            md_message = "### _Error: Speaker file does not exist._"
            is_ui_enabled = False
            return response(md_message, is_ui_enabled)

        try:
            self.model_handler.set_file_paths(
                checkpoint_dir,
                vocab_file,
                config_file
            )
        except Exception as e:
            md_message = "### _Error: One or more model files are invalid or do not exist. Check checkpoint directory, vocab file or config file paths._"
            is_ui_enabled = False
            return response(md_message, is_ui_enabled)

        try:
            self.model_handler.load_model()
            md_message = "### _Model loaded successfully._"
            is_ui_enabled = True
            return response(md_message, is_ui_enabled)

        except Exception as e:
            md_message = f"### _Error: {e}_"
            is_ui_enabled = False
            return response(md_message, is_ui_enabled)
