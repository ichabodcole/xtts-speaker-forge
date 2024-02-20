import os
import torch


class SpeakersHandler:
    def __init__(self, speakers_file):
        self.speakers_file = speakers_file
        if os.path.exists(self.speakers_file) == False:
            print("Speaker file does not exist, creating a new one")

    def get_speakers_list(self):
        speaker_list = []
        if os.path.exists(self.speakers_file):
            speaker_data = torch.load(self.speakers_file)
        else:
            speaker_data = {}

        # Get keys from the speaker embeddings
        for speaker in speaker_data:
            speaker_list.append({
                "id": speaker,
                **speaker_data[speaker]
            })

        return speaker_list

    def get_speaker_names(self):
        if os.path.exists(self.speakers_file):
            speaker_data = torch.load(self.speakers_file)
        else:
            speaker_data = {}

        return list(speaker_data.keys())

    def get_speaker_data(self, speaker_name):
        if os.path.exists(self.speakers_file):
            speaker_data = torch.load(self.speakers_file)
        else:
            return None

        return speaker_data[speaker_name]

    def add_speaker(self, speaker_name, gpt_cond_latent, speaker_embedding, output_path=None):
        if os.path.exists(self.speakers_file):
            speaker_data = torch.load(self.speakers_file)
        else:
            speaker_data = {}

        speaker_data[speaker_name] = {
            gpt_cond_latent,
            speaker_embedding
        }

        if output_path is not None:
            torch.save(speaker_data, output_path)
        else:
            torch.save(speaker_data, self.speakers_file)
