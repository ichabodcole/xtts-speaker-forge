import logging
import argparse
import sys
import gradio as gr
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler
from speaker_forge_explore import SpeakerForgeExplore
from speaker_forge_create import SpeakerForgeCreate
import pathlib
import json
import random

XTTS_MODEL = None

src_dir = pathlib.Path(__file__).parent.resolve()
config_file_name = "app_config.json"
config_file_path = src_dir / config_file_name


print(f"src_dir: {config_file_path}")

with open(config_file_path, "rb") as f:
    app_config = json.load(f)

speaker_file = str(pathlib.Path(src_dir, '../model/speakers_xtts.pth'))
checkpoint_dir = str(pathlib.Path(src_dir, '../model'))
vocab_file = str(pathlib.Path(src_dir, '../model/vocab.json'))
config_file = str(pathlib.Path(src_dir, '../model/config.json'))

speakers_handler = SpeakersHandler(speakers_file=speaker_file)
model_handler = ModelHandler(checkpoint_dir, vocab_file, config_file)
sf_explore = SpeakerForgeExplore(speakers_handler, model_handler)
sf_create = SpeakerForgeCreate(speakers_handler, model_handler)

# define a logger to redirect
default_text_list = [
    "All I want to do is zoom-a-zoom-zoom-zoom and a boom-boom, JUST SHAKE YA RUMP!",
    "Please do not let this extensive clarification distract you from the fact that in 1998, The Undertaker threw Mankind off Hell In A Cell, and plummeted 16 ft through an announcer's table.",
    "Blinded by the light, Rolled up like a douche, in the corner in the right.",
    "I personally believe that U.S. Americans are unable to do so because, uh, some … people out there in our nation don’t have maps and, uh,...",
    "Once you can accept the universe as matter expanding into nothing that is something, wearing stripes with plaid comes easy.",
    "We live in a society exquisitely dependent on science and technology, in which hardly anyone knows anything about science and technology.",
    "It is better to keep your mouth closed and let people think you are a fool than to open it and remove all doubt."
]


def initExploreUI():
    gr.Markdown("_Explore the contents of the XTTS speakers file._")

    load_speakers_btn = gr.Button("Load Speakers")

    with gr.Group(visible=False) as speaker_group:
        speaker_select = gr.Dropdown(
            label="Speaker",
            choices=[]
        )

        # Get a random item from the default_text_list
        text = random.choice(default_text_list)

        speech_text_box = gr.Textbox(
            text,
            label="Speech Text",
            placeholder="Type something...",
            lines=3,
            interactive=True
        )

        generate_speech_btn = gr.Button(
            "Generate Speech")

    with gr.Group(visible=False) as processing_group:
        processing_text = gr.Markdown(
            value="## _Doing the maths n' stuff, please be patient..._"
        )

        audio_player = gr.Audio(
            value=None, format="wav")

    # Setup the button click events
    load_speakers_btn.click(
        sf_explore.load_speaker_data,
        inputs=None,
        outputs=[speaker_group, speaker_select]
    )

    generate_speech_btn.click(
        sf_explore.generate_speech,
        inputs=[speaker_select, speech_text_box],
        outputs=[
            processing_group,
            processing_text,
            generate_speech_btn,
            audio_player
        ]
    ).then(
        sf_explore.do_inference,
        inputs=[speaker_select, speech_text_box],
        outputs=[processing_text, generate_speech_btn, audio_player]
    )


def initCreateUI():
    gr.Markdown("_Create a new speaker from one or more reference wavs/mp3s._")

    with gr.Group():
        file_uploader = gr.File(
            label="Upload Speaker wavs or mp3s",
            type="filepath",
            file_count="multiple",
            file_types=["wav", "mp3"],
            interactive=True
        )

        extract_btn = gr.Button("Create Speaker Embedding")

    with gr.Group(visible=False) as generate_group:
        # Get a random item from the default_text_list
        text = random.choice(default_text_list)

        speech_text_box = gr.Textbox(
            text,
            label="Speech Text",
            placeholder="Type something...",
            lines=3,
            interactive=True
        )

        preview_speaker_btn = gr.Button("Preview Speaker Voice")

    with gr.Group(visible=False) as speaker_audio_group:
        processing_text = gr.Markdown(
            value="## _Doing the maths n' stuff, please be patient..._"
        )

        speaker_audio_player = gr.Audio(
            value=None,
            format="wav",
            interactive=False,
            show_download_button=True
        )

    with gr.Group(visible=False) as save_group:
        speaker_name = gr.Textbox(
            label="Speaker Name",
            placeholder="Enter a unique speaker name and save it to the speaker file.",
            interactive=True
        )

        save_speaker_btn = gr.Button("Save Speaker")

        speaker_saved_message = gr.Markdown(
            value="### _Speaker saved successfully!_",
            visible=False
        )

    # Extracts the speaker embedding from the uploaded audio, then displays the audio player group, but hiding the audio player
    extract_btn.click(
        sf_create.get_speaker_embedding,
        inputs=[file_uploader],
        outputs=[generate_group, speaker_audio_player]
    )

    # Generates the speech from the speaker embedding and the text,
    preview_speaker_btn.click(
        sf_create.generate_speech,
        inputs=[speaker_name],
        outputs=[speaker_audio_group, processing_text, save_group]
    ).then(
        sf_create.do_inference, inputs=[speech_text_box], outputs=[
            processing_text,
            preview_speaker_btn,
            speaker_audio_player,
            save_group
        ]
    )

    save_speaker_btn.click(
        sf_create.save_speaker,
        inputs=[speaker_name],
        outputs=speaker_saved_message
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
    #tab-create-button,
    #tab-explore-button,
    #tab-mix-button,
    #tab-export-button,
    #tab-changelog-button { font-size: 1.5em; }
    """

    with gr.Blocks(css=css) as app:
        gr.Image(value="http://www.gigaglitters.com/created/b7VvpETJqS.gif", elem_id="header-image",
                 image_mode="RGBA", show_download_button=False, container=False, interactive=False)
        gr.Markdown("_v1.0.0_")

        with gr.Tab("Explore", elem_id="tab-explore"):
            with gr.Column():
                initExploreUI()

        with gr.Tab("Create", elem_id="tab-create"):
            with gr.Column():
                initCreateUI()

        with gr.Tab("Mix", elem_id="tab-mix"):
            with gr.Column():
                gr.Markdown("## Mix")

        with gr.Tab("Export", elem_id="tab-export"):
            with gr.Column():
                gr.Markdown("## Export")
        with gr.Tab("Changelog", elem_id="tab-changelog"):
            with gr.Column():
                gr.Markdown("## Changelog")

    app.launch(
        share=False,
        debug=False,
        server_port=args.port,
        server_name="0.0.0.0"
    )
