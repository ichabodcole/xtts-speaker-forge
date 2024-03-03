import os
import time
import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import tempfile
import torchaudio
from utils.utils import is_valid_file_list


class ModelManagerService:
    def __init__(self):
        self.model = None

    def set_file_paths(self, checkpoint_dir: str, vocab_file: str, config_file: str):
        if not is_valid_file_list([checkpoint_dir, vocab_file, config_file]):
            raise FileExistsError(
                "One or more files are invalid or do not exist !!")

        self.checkpoint_dir = checkpoint_dir
        self.vocab_file = vocab_file
        self.config_file = config_file

    def load_model(self):
        if self.model is not None:
            print("Model already loaded")
            return self.model

        self.clear_gpu_cache()

        if not self.checkpoint_dir or not self.config_file or not self.vocab_file:
            raise FileExistsError(
                "You need to run the previous steps or manually set the `XTTS checkpoint path`, `XTTS config path`, and `XTTS vocab path` fields !!")

        config = XttsConfig()
        config.load_json(self.config_file)

        self.model = Xtts.init_from_config(config)

        print("Loading XTTS model! ")

        self.model.load_checkpoint(
            config,
            checkpoint_dir=self.checkpoint_dir,
            vocab_path=self.vocab_file,
            use_deepspeed=False
        )
        if torch.cuda.is_available():
            self.model.cuda()

        return self.model

    def extract_speaker_embedding(self, speaker_audio_files: str):
        if self.model is None:
            print("Loading model... Be Patient.")
            self.load_model()

        gpt_cond_latent, speaker_embedding = self.model.get_conditioning_latents(
            audio_path=speaker_audio_files,
            gpt_cond_len=self.model.config.gpt_cond_len,
            max_ref_length=self.model.config.max_ref_len,
            sound_norm_refs=self.model.config.sound_norm_refs
        )

        return gpt_cond_latent, speaker_embedding

    def run_inference(
        self,
        lang: str,
        tts_text: str,
        gpt_cond_latent: torch.Tensor,
        speaker_embedding: torch.Tensor,
        file_name=None
    ):
        if self.model is None:
            print("Loading model... Be Patient.")
            self.load_model()

        out = self.model.inference(
            text=tts_text,
            language=lang,
            gpt_cond_latent=gpt_cond_latent.to(self.model.device),
            speaker_embedding=speaker_embedding.to(self.model.device),
            temperature=self.model.config.temperature,  # Add custom parameters here
            length_penalty=self.model.config.length_penalty,
            repetition_penalty=self.model.config.repetition_penalty,
            top_k=self.model.config.top_k,
            top_p=self.model.config.top_p,
        )

        # if file_name:
        #     with tempfile.TemporaryDirectory() as temp_dir:
        #         gm_time = time.gmtime()
        #         print("gm_time", gm_time)
        #         out_path = os.path.join(
        #             temp_dir, f"{file_name}.wav")
        #         out["wav"] = torch.tensor(out["wav"]).unsqueeze(0)
        #         torchaudio.save(out_path, out["wav"], 24000)
        #         # Do something with out_path here, e.g., move it to a permanent location
        #         # Note: The temp_dir and its contents are deleted once this block ends,
        #         # so you might want to copy or move the file to another location if you
        #         # want to keep it.
        # else:
        # Use a temporary file which will be automatically deleted unless delete=False
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            out_path = temp_file.name
            out["wav"] = torch.tensor(out["wav"]).unsqueeze(0)
            torchaudio.save(out_path, out["wav"], 24000)
            # The temp_file is not deleted automatically because delete=False
            # You can access it using out_path

        return out_path

    def clear_gpu_cache(self):
        # clear the GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
