import os
import torch

from utils.utils import is_valid_file


class SpeakersHandler:
    speakers_data = None
    speakers_file = None

    def __init__(self):
        pass

    def set_speaker_file(self, speakers_file):
        if not is_valid_file(speakers_file):
            raise FileExistsError("Speaker file does not exist")

        self.speakers_file = speakers_file
        self.load_speaker_file_data()

        return self.speakers_file

    def get_speakers_list(self):
        speaker_list = []

        # Get keys from the speaker embeddings
        for speaker in self.speakers_data:
            speaker_list.append({
                "id": speaker,
                **self.speakers_data[speaker]
            })

        return speaker_list

    def get_speaker_names(self):
        return list(self.speakers_data.keys())

    def get_speaker_data(self, speaker_name):
        return self.speakers_data[speaker_name]

    def add_speaker(self, speaker_name, gpt_cond_latent, speaker_embedding, output_path=None):
        self.speakers_data[speaker_name] = {
            "gpt_cond_latent": gpt_cond_latent,
            "speaker_embedding": speaker_embedding
        }

    def remove_speaker(self, speaker_name):
        if speaker_name in self.speakers_data:
            del self.speakers_data[speaker_name]
        else:
            print(f"Speaker {speaker_name} does not exist")

    def save_speaker_file(self, output_path=None):
        if output_path is not None:
            torch.save(self.speakers_data, output_path)
        else:
            torch.save(self.speakers_data, self.speakers_file)

    def load_speaker_file_data(self):
        if self.speakers_data is not None:
            return

        if self.speakers_file and os.path.exists(self.speakers_file):
            self.speakers_data = torch.load(self.speakers_file)
        else:
            print("Speaker file does not exist")
            raise FileExistsError("Speaker file does not exist")
