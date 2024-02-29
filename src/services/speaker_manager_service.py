import os
import pathlib
import time
import torch
from types_module import SpeakerEmbedding, SpeakerEmbeddingList, SpeakerFileData, SpeakerMetadata, SpeakerWeightsList
from utils.utils import is_valid_file
from utils.embedding_utils import CombineMethod, average_latents_and_embeddings


class SpeakerManagerService:
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
        names = list(self.speakers_file_data.keys())
        names.sort()

        return names

    def get_speaker_data(self, speaker_name):
        if speaker_name in self.speakers_file_data:
            return self.speakers_file_data[speaker_name]

        return None

    def add_speaker(self, speaker_name, gpt_cond_latent, speaker_embedding, output_path=None):
        self.speakers_file_data[speaker_name] = {
            "gpt_cond_latent": gpt_cond_latent,
            "speaker_embedding": speaker_embedding
        }

    def update_speaker_name(self, old_speaker_name, new_speaker_name):
        if old_speaker_name in self.speakers_file_data:
            self.speakers_file_data[new_speaker_name] = self.speakers_file_data.pop(
                old_speaker_name)
        else:
            print(f"Speaker {old_speaker_name} does not exist")

    def update_speaker_meta(self, speaker_name, metadata: SpeakerMetadata = None):
        if speaker_name in self.speakers_file_data:
            if metadata is not None:
                new_speaker_name = metadata.get("speaker_name", None)

                if new_speaker_name is None:
                    return

                new_speaker_name = str(new_speaker_name).strip()

                if new_speaker_name != "":
                    self.speakers_file_data[speaker_name]["metadata"] = metadata

                    # print(f"Updated speaker {speaker_name} with metadata {metadata}")

                    self.update_speaker_name(speaker_name, new_speaker_name)
        else:
            print(f"Speaker {speaker_name} does not exist")

    def get_speaker_metadata(self, speaker_name) -> SpeakerMetadata | None:
        if speaker_name in self.speakers_file_data:
            speaker = self.speakers_file_data[speaker_name]
            if "metadata" in speaker:
                return speaker["metadata"]

        return None

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
        if self.speakers_file_data is not None:
            return self.speakers_file_data

        if self.speakers_file and os.path.exists(self.speakers_file):
            return torch.load(self.speakers_file)
        else:
            print("Speaker file does not exist")
            raise FileExistsError("Speaker file does not exist")

    def create_speaker_file_from_selected_speakers(self, selected_speakers: list[str]):
        speaker_file_data = {}
        time_seconds = int(time.time())

        for speaker in selected_speakers:
            if speaker in self.speakers_file_data:
                speaker_file_data[speaker] = self.speakers_file_data[speaker]

        speaker_file_dir = pathlib.Path(self.speakers_file).parent.resolve()

        out_path = os.path.join(
            speaker_file_dir, 'speaker_forge', f"speakers_xtts_sf_{str(time_seconds)}.pth")

        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

        torch.save(speaker_file_data, out_path)

        return out_path