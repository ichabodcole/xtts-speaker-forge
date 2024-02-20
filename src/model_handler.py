import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import tempfile
import torchaudio


class ModelHandler:
    def __init__(self, checkpoint_dir, vocab_file, config_file):
        self.model = None
        self.checkpoint_dir = checkpoint_dir
        self.vocab_file = vocab_file
        self.config_file = config_file

    def load_model(self):
        if self.model is not None:
            print("Model already loaded")
            return self.model

        self.clear_gpu_cache()

        if not self.checkpoint_dir or not self.config_file or not self.vocab_file:
            return "You need to run the previous steps or manually set the `XTTS checkpoint path`, `XTTS config path`, and `XTTS vocab path` fields !!"

        config = XttsConfig()
        config.load_json(self.config_file)

        self.model = Xtts.init_from_config(config)

        print("Loading XTTS model! ")

        self.model.load_checkpoint(
            config, checkpoint_dir=self.checkpoint_dir, vocab_path=self.vocab_file, use_deepspeed=False)
        if torch.cuda.is_available():
            self.model.cuda()

        return self.model

    def extract_speaker_embedding(self, speaker_audio_files):
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

    def run_inference(self, lang, tts_text, gpt_cond_latent, speaker_embedding):
        if self.model is None:
            print("Loading model... Be Patient.")
            self.load_model()

        out = self.model.inference(
            text=tts_text,
            language=lang,
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=self.model.config.temperature,  # Add custom parameters here
            length_penalty=self.model.config.length_penalty,
            repetition_penalty=self.model.config.repetition_penalty,
            top_k=self.model.config.top_k,
            top_p=self.model.config.top_p,
        )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
            out["wav"] = torch.tensor(out["wav"]).unsqueeze(0)
            out_path = fp.name
            torchaudio.save(out_path, out["wav"], 24000)

        return out_path

    def clear_gpu_cache(self):
        # clear the GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
