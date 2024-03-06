import os
import pathlib
import time
from typing import Dict
import torch
from constants.common import SPEAKER_METADATA_KEY
from types_module import SpeakerData, SpeakerEmbeddingList, SpeakerFileData, SpeakerMetadata, SpeakerWeightsList
from utils.utils import is_valid_file
from utils.embedding_utils import CombineMethod, average_latents_and_embeddings


class SpeakerManagerService:
    speakers_file_data: SpeakerFileData = None
    speakers_file: str = None

    def set_speaker_file(self, speakers_file: str):
        if not is_valid_file(speakers_file):
            raise FileExistsError("Speaker file does not exist")

        self.speakers_file = speakers_file
        self.speakers_file_data = self.load_speaker_file_data()
        self.speakers_file_data = self.update_speaker_file_data_format()

        return self.speakers_file

    def get_speaker_file(self):
        return self.speakers_file

    def get_speaker_names(self):
        if self.speakers_file_data is None:
            return []

        names = list(self.speakers_file_data.keys())
        names = list(filter(lambda name: name != SPEAKER_METADATA_KEY, names))
        names.sort()

        return names

    def get_speaker_data(self, speaker_name):
        if speaker_name in self.speakers_file_data:
            return self.speakers_file_data[speaker_name]

        return None

    def add_speaker(
        self,
        speaker_name: str,
        gpt_cond_latent: torch.Tensor,
        speaker_embedding: torch.Tensor,
        metadata: SpeakerMetadata = None
    ):
        self.speakers_file_data[speaker_name] = {
            "gpt_cond_latent": gpt_cond_latent,
            "speaker_embedding": speaker_embedding,
        }

        if metadata is not None:
            self.set_speaker_metadata(speaker_name, metadata)

    def update_speaker_name(self, old_speaker_name: str, new_speaker_name: str):
        if old_speaker_name in self.speakers_file_data:
            self.speakers_file_data[new_speaker_name] = self.speakers_file_data.pop(
                old_speaker_name)
        else:
            print(f"Speaker {old_speaker_name} does not exist")

    def update_speaker_meta(self, speaker_name: str, speaker_metadata: SpeakerMetadata = None):
        if speaker_name in self.speakers_file_data:
            if speaker_metadata is not None:
                new_speaker_name = speaker_metadata.get("speaker_name", None)

                if new_speaker_name is None:
                    return

                new_speaker_name = str(new_speaker_name).strip()

                if new_speaker_name != "":
                    self.set_speaker_metadata(
                        new_speaker_name, speaker_metadata)

                    # print(f"Updated speaker {speaker_name} with metadata {speaker_metadata}")
                    self.update_speaker_name(speaker_name, new_speaker_name)
        else:
            print(f"Speaker {speaker_name} does not exist")

    def get_speaker_metadata(self, speaker_name: str) -> SpeakerMetadata | None:
        if speaker_name in self.get_metadata():
            return self.get_metadata().get(speaker_name)

        return None

    def set_speaker_metadata(self, speaker_name: str, metadata: SpeakerMetadata):
        self.speakers_file_data.setdefault(SPEAKER_METADATA_KEY, {})[
            speaker_name] = metadata

    def get_metadata(self) -> Dict[str, SpeakerMetadata]:
        return self.speakers_file_data.get(SPEAKER_METADATA_KEY, {})

    def remove_speaker(self, speaker_name: str):
        if speaker_name in self.speakers_file_data:
            del self.speakers_file_data[speaker_name]
        else:
            print(f"Speaker {speaker_name} does not exist")

        if speaker_name in self.get_metadata():
            del self.speakers_file_data[SPEAKER_METADATA_KEY][speaker_name]

    def save_speaker_file(self, output_path: str | None = None):
        if output_path is not None:
            torch.save(self.speakers_file_data, output_path)
        else:
            torch.save(self.speakers_file_data, self.speakers_file)

    def create_speaker_embedding_from_mix(self, speaker_weights: SpeakerWeightsList, combine_method: CombineMethod = CombineMethod.MEAN) -> SpeakerData:
        latent_embedding_pairs = []
        weights = []

        # print("create_speaker_embedding_from_mix:", self.speaker_weights)

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
        if self.speakers_file and os.path.exists(self.speakers_file):
            return torch.load(self.speakers_file)
        else:
            print("Speaker file does not exist")
            raise FileExistsError("Speaker file does not exist")

    def update_speaker_file_data_format(self):
        if self.speakers_file_data is None:
            raise ValueError("Speaker file data is not loaded")

        new_metadata = self.get_metadata()

        for speaker in self.speakers_file_data:
            # Convert old metadata to new format
            if 'metadata' in self.speakers_file_data.get(speaker, {}):
                old_metadata = self.speakers_file_data[speaker]['metadata']

                if old_metadata and (speaker not in new_metadata):
                    new_metadata[speaker] = old_metadata

        self.speakers_file_data[SPEAKER_METADATA_KEY] = new_metadata

        return self.speakers_file_data

    def import_speakers_from_file(self, file_path: str) -> SpeakerFileData | None:
        if not is_valid_file(file_path):
            raise FileExistsError("Speaker file does not exist")

        try:
            speaker_data = torch.load(file_path)
            if type(speaker_data) == dict:
                return speaker_data
            else:
                print("Invalid speaker file")
                return None
        except Exception as e:
            print(f"Error loading speaker file: {e}")
            return None

    def tensor_to_cpu(self, speaker_embedding: torch.Tensor):
        if speaker_embedding.is_cuda:
            return speaker_embedding.cpu()

        return speaker_embedding

    def create_speaker_file_from_selected_speakers(self, selected_speakers: list[str]):
        news_speaker_file_data: SpeakerFileData = {
            SPEAKER_METADATA_KEY: {}
        }

        time_seconds = int(time.time())

        for speaker in selected_speakers:
            if speaker in self.speakers_file_data:
                news_speaker_file_data[speaker] = {}

                gpu_cond_latent = self.speakers_file_data[speaker].get(
                    "gpt_cond_latent"
                )

                speaker_embedding = self.speakers_file_data[speaker].get(
                    "speaker_embedding"
                )

                news_speaker_file_data[speaker]["gpt_cond_latent"] = self.tensor_to_cpu(
                    gpu_cond_latent
                )

                news_speaker_file_data[speaker]["speaker_embedding"] = self.tensor_to_cpu(
                    speaker_embedding
                )

                if speaker in self.get_metadata():
                    news_speaker_file_data[SPEAKER_METADATA_KEY][speaker] = self.get_speaker_metadata(
                        speaker)

        speaker_file_dir = pathlib.Path(self.speakers_file).parent.resolve()

        out_path = os.path.join(
            speaker_file_dir, 'speaker_forge', f"speakers_xtts_sf_{str(time_seconds)}.pth")

        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

        torch.save(news_speaker_file_data, out_path)

        return out_path
