import os
import logging
import argparse
import sys
import gradio as gr
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler
import pathlib
import json
from create_ui import CreateUI
from explore_ui import ExploreUI
from setup_ui import SetupUI
from mix_ui import MixUI

src_dir = pathlib.Path(__file__).parent.resolve()
config_file_name = "app_config.json"
config_file_path = src_dir / config_file_name

checkpoint_dir = os.environ.get("CHECKPOINT_DIR")
config_file = os.environ.get("CONFIG_PATH")
vocab_file = os.environ.get("VOCAB_PATH")
speaker_file = os.environ.get("SPEAKERS_XTTS_PATH")

if not checkpoint_dir:
    raise ValueError("CHECKPOINT_DIR environment variable not set")
if not config_file:
    raise ValueError("CONFIG_PATH environment variable not set")
if not vocab_file:
    raise ValueError("VOCAB_PATH environment variable not set")
if not speaker_file:
    raise ValueError("SPEAKER_PATH environment variable not set")

speakers_handler = SpeakersHandler()
speakers_handler.set_speaker_file(speaker_file)

model_handler = ModelHandler()
setup_ui = SetupUI(speakers_handler, model_handler)
explore_ui = ExploreUI(speakers_handler, model_handler)
create_ui = CreateUI(speakers_handler, model_handler)
mix_ui = MixUI(speakers_handler, model_handler)


class Logger:
    def __init__(self, filename="log.out"):
        self.log_file = filename
        self.terminal = sys.stdout
        self.log = open(self.log_file, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def isatty(self):
        return False


# redirect stdout and stderr to a file
sys.stdout = Logger()
sys.stderr = sys.stdout

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


def read_logs():
    sys.stdout.flush()
    with open(sys.stdout.log_file, "r") as f:
        return f.read()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""XTTS Speaker Forge\n\n"""
        """
        Example runs:
        python3 src/speaker_forge.py --port 
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--port",
        type=int,
        help="Port to run the gradio demo. Default: 5003",
        default=5003,
    )

    # parser.add_argument(
    #     "--out_path",
    #     type=str,
    #     help="Output path updated speaker_xtts.pth file will be saved Default: /tmp/xtts_speaker_forge/",
    #     default="/tmp/xtts_speaker_forge/",
    # )

    # parser.add_argument(
    #     "--max_audio_length",
    #     type=int,
    #     help="Max permitted audio size in seconds. Default: 11",
    #     default=11,
    # )

    args = parser.parse_args()

    css = """
    #header-image { text-align: center; }
    #header-image button { display: flex; justify-content: center; pointer-events: none; }
    #header-image img { max-width: 876px }
    .tab-nav button { font-size: 1.5em; }
    .tab-nav button.selected { --body-text-color: rgb(103 232 249); }
    .processing-text { padding-left: 10px; }
    .section-description { 
        --body-text-color: rgb(103 232 249);
        font-size: 1.1em; 
        margin-top: 5px; 
        margin-left: 5px;
    }
    """

    with gr.Blocks(css=css) as app:
        # https://i.postimg.cc/rpbTgB2y/b7-Vvp-ETJq-S.gif
        # http://www.gigaglitters.com/created/b7VvpETJqS.gif
        gr.Image(value="http://www.gigaglitters.com/created/b7VvpETJqS.gif", elem_id="header-image",
                 image_mode="RGBA", show_download_button=False, container=False, interactive=False)
        gr.Markdown("_v1.0.0_")

        with gr.Tab("Setup", elem_id="tab-setup"):
            with gr.Column():
                setup_data = setup_ui.createUI(
                    checkpoint_dir,
                    vocab_file,
                    config_file,
                    speaker_file
                )

        with gr.Tab("Explore", elem_id="tab-explore", interactive=False) as explore_tab:
            with gr.Column():
                explore_ui.createIU()

        with gr.Tab("Create", elem_id="tab-create", interactive=False) as create_tab:
            with gr.Column():
                create_ui.createUI()

        with gr.Tab("Mix", elem_id="tab-mix", interactive=False) as mix_tab:
            with gr.Column():
                mix_ui.createUI()
                pass

        with gr.Tab("Export", elem_id="tab-export", interactive=False) as export_tab:
            with gr.Column():
                # initExportUI()
                pass

        with gr.Tab("Changelog", elem_id="tab-changelog"):
            with gr.Column():
                gr.Markdown(
                    value="_Read the exciting development updates!_",
                    elem_classes=["section-description"]
                )

        # TODO: Look for a cleaner way to do this
        setup_data['load_btn'].click(
            setup_ui.validate_paths_and_load_model,
            inputs=[
                setup_data["checkpoint_dir"],
                setup_data["vocab_file"],
                setup_data["config_file"],
                setup_data["speaker_file"]
            ],
            outputs=[
                setup_data["message"],
                explore_tab,
                create_tab,
                mix_tab,
                export_tab
            ]
        )

    app.launch(
        share=False,
        debug=False,
        server_port=args.port,
        server_name="0.0.0.0"
    )
