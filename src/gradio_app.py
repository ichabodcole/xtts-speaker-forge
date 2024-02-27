import os
import logging
import argparse
import sys
import gradio as gr
from content_handler import ContentHandler
from css import app_css
from forge_about_view import ForgeAboutView
from forge_changelog_view import ForgeChangelogView
from forge_export_view import ForgeExportView
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler
import pathlib
from forge_create_view import ForgeCreateView
from forge_explore_view import ForgeExploreView
from forge_setup_view import ForgeSetupView
from forge_mix_view import ForgeMixView
from utils.utils import get_latest_changelog_version

latest_version = get_latest_changelog_version()
src_dir = pathlib.Path(__file__).parent.resolve()
assets_dir = src_dir / "assets"
content_file_path = src_dir / "content.json"

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


content_handler = ContentHandler(content_file_path)
speakers_handler = SpeakersHandler()
speakers_handler.set_speaker_file(speaker_file)

model_handler = ModelHandler()
setup_view = ForgeSetupView(
    speakers_handler,
    model_handler,
    content_handler
)
setup_view.set_file_paths(
    checkpoint_dir,
    vocab_file,
    config_file,
    speaker_file
)

explore_view = ForgeExploreView(
    speakers_handler,
    model_handler,
    content_handler
)

create_view = ForgeCreateView(
    speakers_handler,
    model_handler,
    content_handler
)

mix_view = ForgeMixView(
    speakers_handler,
    model_handler,
    content_handler
)

export_view = ForgeExportView(
    speakers_handler,
    model_handler,
    content_handler
)

changelog_view = ForgeChangelogView(
    speakers_handler,
    model_handler,
    content_handler
)

about_view = ForgeAboutView(
    speakers_handler,
    model_handler,
    content_handler
)


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

    parser.add_argument(
        "--share",
        type=bool,
        help="Share the gradio demo. Default: False",
        default=False,
    )

    # TODO: limit create views audio upload size...
    # parser.add_argument(
    #     "--max_audio_length",
    #     type=int,
    #     help="Max permitted audio size in seconds. Default: 11",
    #     default=11,
    # )

    args = parser.parse_args()

    explore_tab = gr.Tab(
        label="Explore",
        elem_id="tab-explore",
        interactive=False, render=False
    )
    create_tab = gr.Tab(
        label="Create",
        elem_id="tab-create",
        interactive=False,
        render=False
    )
    mix_tab = gr.Tab(
        label="Mix",
        elem_id="tab-mix",
        interactive=False,
        render=False
    )
    export_tab = gr.Tab(
        label="Export",
        elem_id="tab-export",
        interactive=False,
        render=False
    )

    setup_view.set_tabs(explore_tab, create_tab, mix_tab, export_tab)

    with gr.Blocks(css=app_css()) as app:
        # https://i.postimg.cc/dDMzdf2g/speaker-forge-glitter.gif
        # http://www.gigaglitters.com/created/b7VvpETJqS.gif

        gr.Markdown("# _XTTS_", elem_classes=['xtts-header'])
        gr.Image(value="https://i.postimg.cc/dDMzdf2g/speaker-forge-glitter.gif", elem_id="header-image",
                 image_mode="RGBA", show_download_button=False, container=False, interactive=False)
        gr.Markdown(f"_v{latest_version}_")

        with gr.Tab("Setup", elem_id="tab-setup"):
            with gr.Column():
                setup_view.init_ui()

        with explore_tab.render():
            with gr.Column():
                explore_view.init_ui()

        with create_tab.render():
            with gr.Column():
                create_view.init_ui()

        with mix_tab.render():
            with gr.Column():
                mix_view.init_ui()

        with export_tab.render():
            with gr.Column():
                export_view.init_ui()

        with gr.Tab("Changelog", elem_id="tab-changelog"):
            with gr.Column():
                changelog_view.init_ui()

        with gr.Tab("About", elem_id="tab-about"):
            with gr.Column():
                about_view.init_ui()

    app.launch(
        share=args.share,
        debug=False,
        server_port=args.port,
        server_name="0.0.0.0"
    )
