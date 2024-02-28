from typing import List, Dict, Tuple
from typing_extensions import TypedDict
import gradio as gr
import torch


class SpeakerWeight(TypedDict):
    speaker: str
    weight: int


SpeakerWeightsList = List[SpeakerWeight]


class SpeakerEmbedding(TypedDict):
    gpt_cond_latent: torch.Tensor
    speaker_embedding: torch.Tensor


SpeakerFileData = Dict[str, SpeakerEmbedding]


class SpeakerEntry(SpeakerEmbedding):
    id: str


SpeakerEmbeddingList = List[SpeakerEntry]

SliderList = List[gr.Slider]

SpeakerNameList = List[str]

EmbeddingPair = Tuple[torch.Tensor, torch.Tensor]

EmbeddingPairsList = List[EmbeddingPair]


class SpeakerMetadata(TypedDict):
    speaker_name: str | None
    age_range: str | None
    gender: str | None
    accent: str | None
    tonal_quality: List[str] | None
    style: List[str] | None
    genre: List[str] | None
    character_type: List[str] | None
    description: str | None
