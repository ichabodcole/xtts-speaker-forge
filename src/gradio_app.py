import os
import logging
import argparse
import sys
import gradio as gr
from services.content_manager_service import ContentManagerService
from css import app_css
from views.forge_about_view import ForgeAboutView
from views.forge_changelog_view import ForgeChangelogView
from views.forge_edit_view import ForgeEditView
from views.forge_export_view import ForgeExportView
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService
import pathlib
from views.forge_create_view import ForgeCreateView
from views.forge_explore_view import ForgeExploreView
from views.forge_import_view import ForgeImportView
from views.forge_setup_view import ForgeSetupView
from views.forge_mix_view import ForgeMixView
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


content_service = ContentManagerService(content_file_path)
speaker_service = SpeakerManagerService()

model_service = ModelManagerService()
setup_view = ForgeSetupView(
    speaker_service,
    model_service,
    content_service
)
setup_view.set_file_paths(
    checkpoint_dir,
    vocab_file,
    config_file,
    speaker_file
)

explore_view = ForgeExploreView(
    speaker_service,
    model_service,
    content_service
)

create_view = ForgeCreateView(
    speaker_service,
    model_service,
    content_service
)

mix_view = ForgeMixView(
    speaker_service,
    model_service,
    content_service
)

edit_view = ForgeEditView(
    speaker_service,
    model_service,
    content_service
)

import_view = ForgeImportView(
    speaker_service,
    model_service,
    content_service
)

export_view = ForgeExportView(
    speaker_service,
    model_service,
    content_service
)

changelog_view = ForgeChangelogView(
    speaker_service,
    model_service,
    content_service
)

about_view = ForgeAboutView(
    speaker_service,
    model_service,
    content_service
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
    edit_tab = gr.Tab(
        label="Edit",
        elem_id="tab-edit",
        interactive=False,
        render=False
    )
    import_tab = gr.Tab(
        label="Import",
        elem_id="tab-import",
        interactive=False,
        render=False
    )
    export_tab = gr.Tab(
        label="Export",
        elem_id="tab-export",
        interactive=False,
        render=False
    )

    setup_view.set_tabs(
        explore_tab,
        create_tab,
        mix_tab,
        edit_tab,
        import_tab,
        export_tab
    )

    with gr.Blocks(css=app_css()) as app:
        # https://i.postimg.cc/dDMzdf2g/speaker-forge-glitter.gif
        # http://www.gigaglitters.com/created/b7VvpETJqS.gif

        gr.Markdown("# _XTTS_", elem_classes=['xtts-header'])
        # gr.Image(value="https://i.postimg.cc/dDMzdf2g/speaker-forge-glitter.gif", elem_id="header-image",
        #          image_mode="RGBA", show_download_button=False, container=False, interactive=False)
        gr.HTML("""
                <div id="header-image">
                    <img src="https://i.postimg.cc/dDMzdf2g/speaker-forge-glitter.gif" alt="XTTS Speaker Forge">
                </div>
                """)
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

        with edit_tab.render():
            with gr.Column():
                edit_view.init_ui()

        with import_tab.render():
            with gr.Column():
                import_view.init_ui()

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
        server_name="0.0.0.0",
        ssr_mode=False  # Disable SSR mode for Gradio 5 compatibility
    )
