import torch
from enum import Enum
from typing import List


class CombineMethod(Enum):
    MEAN = 'mean'
    SUM = 'sum'
    MEDIAN = 'median'
    MAX = 'max'
    MIN = 'min'
    NORMALIZED_SUM = 'normalized_sum'


def average_latents_and_embeddings(latent_embedding_pairs, combine_method: CombineMethod = CombineMethod.MEAN, speaker_weights: List | None = None):
    """
    Averages a list of (gpt_cond_latents, speaker_embedding) pairs.

    Args:
        latent_embedding_pairs (list of tuples): A list where each element is a tuple containing gpt_cond_latents and speaker_embedding.
    Returns:
        tuple: A tuple containing the averaged gpt_cond_latents and speaker_embedding.
    """

    # Separate gpt_cond_latents and speaker_embeddings
    gpt_cond_latents_list = [pair[0] for pair in latent_embedding_pairs]
    speaker_embeddings_list = [pair[1] for pair in latent_embedding_pairs]

    # Average gpt_cond_latents
    avg_gpt_cond_latents = combine_embeddings(
        gpt_cond_latents_list, combine_method, speaker_weights)

    # Average speaker_embeddings
    avg_speaker_embedding = combine_embeddings(
        speaker_embeddings_list, combine_method, speaker_weights)

    return avg_gpt_cond_latents, avg_speaker_embedding


def combine_embeddings(embeddings, method, weights: List | None = None):
    if weights is None:
        weights = [1 for _ in embeddings]

    if len(weights) != len(embeddings):
        raise ValueError(
            "Weights match the number of embeddings for weighted average.")

    weighted_embeddings = [
        embedding * weight for embedding, weight in zip(embeddings, weights)]

    if method == CombineMethod.MEAN:
        return torch.mean(torch.stack(weighted_embeddings), dim=0)
    elif method == CombineMethod.SUM:
        return torch.sum(torch.stack(weighted_embeddings), dim=0)
    elif method == CombineMethod.MEDIAN:
        return torch.median(torch.stack(weighted_embeddings), dim=0).values
    elif method == CombineMethod.MAX:
        return torch.max(torch.stack(weighted_embeddings), dim=0).values
    elif method == CombineMethod.MIN:
        return torch.min(torch.stack(weighted_embeddings), dim=0).values
    elif method == CombineMethod.NORMALIZED_SUM:
        normalized = [embedding / torch.norm(embedding)
                      for embedding in weighted_embeddings]
        return torch.sum(torch.stack(normalized), dim=0)
    else:
        raise ValueError("Invalid combine method specified.")


def normalize_weights(weights):
    total = sum(weights)
    if total == 0:
        raise ValueError("Sum of weights cannot be zero.")
    return [w / total for w in weights]