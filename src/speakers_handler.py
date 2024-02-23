import os
from typing import Tuple
import torch
from types_module import EmbeddingPair, SpeakerEmbedding, SpeakerEmbeddingList, SpeakerFileData, SpeakerWeightsList
from utils.utils import is_valid_file
from utils.embedding_utils import CombineMethod, average_latents_and_embeddings


class SpeakersHandler:
    speakers_file_data: SpeakerFileData = None
    speakers_file: str = None

    def set_speaker_file(self, speakers_file):
        if not is_valid_file(speakers_file):
            raise FileExistsError("Speaker file does not exist")

        self.speakers_file = speakers_file
        self.speakers_file_data = self.load_speaker_file_data()

        return self.speakers_file

    def get_speakers_list(self):
        speaker_list: SpeakerEmbeddingList = []

        # Get keys from the speaker embeddings
        for speaker in self.speakers_file_data:
            speaker_list.append({
                "id": speaker,
                **self.speakers_file_data[speaker]
            })

        return speaker_list

    def get_speaker_names(self):
        return list(self.speakers_file_data.keys())

    def get_speaker_data(self, speaker_name):
        return self.speakers_file_data[speaker_name]

    def add_speaker(self, speaker_name, gpt_cond_latent, speaker_embedding, output_path=None):
        self.speakers_file_data[speaker_name] = {
            "gpt_cond_latent": gpt_cond_latent,
            "speaker_embedding": speaker_embedding
        }

    def remove_speaker(self, speaker_name):
        if speaker_name in self.speakers_file_data:
            del self.speakers_file_data[speaker_name]
        else:
            print(f"Speaker {speaker_name} does not exist")

    def save_speaker_file(self, output_path=None):
        if output_path is not None:
            torch.save(self.speakers_file_data, output_path)
        else:
            torch.save(self.speakers_file_data, self.speakers_file)

    def create_speaker_embedding_from_mix(self, speaker_weights: SpeakerWeightsList, combine_method: CombineMethod = CombineMethod.MEAN) -> SpeakerEmbedding:
        latent_embedding_pairs = []
        weights = []

        # Map speaker weights for easy lookup
        speaker_weight_map = {
            sw['speaker']: sw['weight'] for sw in speaker_weights
        }

        for speaker, embedding_data in self.speakers_file_data.items():
            if speaker in speaker_weight_map:
                # Append the (latents, embeddings) tuple
                latent_embedding_pairs.append(
                    (embedding_data['gpt_cond_latent'], embedding_data['speaker_embedding']))
                # Append the corresponding weight
                weights.append(speaker_weight_map[speaker])

        # Adjustments may be needed if the function's logic for handling weights is different from expected
        avg_gpt_cond_latents, avg_speaker_embedding = average_latents_and_embeddings(
            latent_embedding_pairs, combine_method, speaker_weights=weights)

        return {
            "gpt_cond_latent": avg_gpt_cond_latents,
            "speaker_embedding": avg_speaker_embedding
        }

    def load_speaker_file_data(self) -> SpeakerFileData:
        if self.speakers_file_data is not None:
            return self.speakers_file_data

        if self.speakers_file and os.path.exists(self.speakers_file):
            return torch.load(self.speakers_file)
        else:
            print("Speaker file does not exist")
            raise FileExistsError("Speaker file does not exist")
