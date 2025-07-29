from typing import List, Optional, Literal
from pydantic import BaseModel

import numpy as np
from sentence_transformers import SentenceTransformer
from sentencex import segment


class CVS:
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        """
        Initialize the CVS (Coherent Vector Space) segmenter.

        Args:
            model_name: Name of the sentence transformer model to use for embeddings.
        """
        self.model_name = model_name
        self.sentence_transformer = SentenceTransformer(model_name)

    def get_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text to segment into sentences.

        Returns:
            List of sentences.
        """
        return list(segment("en", text))

    def _calculate_segment_score(
        self, embeddings: np.ndarray, start: int, end: int
    ) -> float:
        """
        Calculate the coherence score for a text segment based on embeddings.

        Args:
            embeddings: Sentence embeddings.
            start: Start index of the segment.
            end: End index of the segment.

        Returns:
            Segment score (lower is better).
        """
        if end - start < 2:
            return float("inf")

        segment = embeddings[start:end]
        segment_mean = np.mean(segment, axis=0)

        # Calculate intra-segment cohesion (average cosine similarity within the segment)
        intra_cohesion = float(np.mean(
            [
                np.dot(segment[i], segment_mean)
                / (np.linalg.norm(segment[i]) * np.linalg.norm(segment_mean))
                for i in range(len(segment))
            ]
        ))

        return -intra_cohesion  # We negate it because we want to minimize the score

    def _dp_segment(self, embeddings: np.ndarray, penalty: float) -> List[int]:
        """
        Segment text using dynamic programming approach.

        Args:
            embeddings: Sentence embeddings.
            penalty: Penalty for introducing a new segment.

        Returns:
            List of segment end indices.
        """
        N = len(embeddings)

        # Initialize score and backtrack tables
        score_table = np.full(N, float("inf"))
        back_table = np.zeros(N, dtype=int)

        # Fill the score table for the first segment
        for i in range(N):
            score_table[i] = self._calculate_segment_score(embeddings, 0, i + 1)

        # Fill the rest of the score table
        for i in range(1, N):
            for j in range(i):
                score = (
                    score_table[j]
                    + self._calculate_segment_score(embeddings, j + 1, i + 1)
                    + penalty
                )
                if score < score_table[i]:
                    score_table[i] = score
                    back_table[i] = j + 1

        # Backtrack to find the optimal segmentation points
        splits = []
        pos = N - 1
        while pos > 0:
            pos = back_table[pos] - 1
            splits.append(pos + 1)

        return sorted(splits + [N])

    def _greedy_segment(self, embeddings: np.ndarray, penalty: float) -> List[int]:
        """
        Segment text using greedy approach.

        Args:
            embeddings: Sentence embeddings.
            penalty: Penalty for introducing a new segment.

        Returns:
            List of segment end indices.
        """
        N = len(embeddings)
        splits = [N]

        while True:
            best_score = float("inf")
            best_split = None

            for i in range(1, N - 1):
                if i in splits:
                    continue

                current_splits = sorted(splits + [i])
                score = sum(
                    self._calculate_segment_score(embeddings, start, end)
                    for start, end in zip([0] + current_splits[:-1], current_splits)
                )
                score += penalty * (len(current_splits) - 1)

                if score < best_score:
                    best_score = score
                    best_split = i

            if best_split is None or best_score >= float("inf"):
                break

            splits.append(best_split)

        return sorted(splits)

    def _naive_segment(self, length: int, num_segments: int) -> List[int]:
        """
        Naive equal-length segmentation.

        Args:
            length: Number of sentences.
            num_segments: Number of desired segments.

        Returns:
            List of segment end indices.
        """
        segment_size = length // num_segments
        splits = []
        for i in range(1, num_segments):
            split_point = i * segment_size
            if split_point < length:
                splits.append(split_point)
        splits.append(length)
        return splits

    def segment_text(
        self,
        sentences: List[str],
        method: str = "cvs",
        strategy: Literal["dp", "greedy"] = "dp",
        num_segments: Optional[int] = None,
        # return_segments: bool = True
    ) -> List[str]: # Union[np.ndarray, List[List[str]]]
        """
        Segment text using the specified method.

        Args:
            sentences: List of sentences.
            method: 'cvs', 'similarity', or 'naive'.
            strategy: 'dp' or 'greedy' (for CVS only).
            num_segments: Number of desired segments.
            return_segments: If True, return the segmented text instead of a binary segmentation vector.

        Returns:
            If return_segments is False:
                Binary numpy array where 1 indicates a segment boundary.
            If return_segments is True:
                List of segments, where each segment is a list of sentences.
        """
        if len(sentences) < 2:
            return [" ".join(sentences)] #if return_segments else np.zeros(len(sentences))

        if num_segments is None:
            num_segments = max(2, len(sentences) // 2)

        if method == "naive":
            splits = self._naive_segment(len(sentences), num_segments)
        else:
            embeddings = self.sentence_transformer.encode(sentences)
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms

            if method == "cvs":
                splits = (
                    self._dp_segment(embeddings, 0.1)
                    if strategy == "dp"
                    else self._greedy_segment(embeddings, 0.1)
                )
            else:
                raise NotImplementedError(f"Method {method} is not implemented.")

        # if return_segments:
        
        # Return segments
        splits = sorted(splits)  # Ensure splits are in order
        segments = [
            " ".join(sentences[start:end]) for start, end in zip([0] + splits[:-1], splits)
        ]
        return segments

        # Otherwise, return binary segmentation vector
        # segmentation = np.zeros(len(sentences))
        # for split in splits[:-1]:
        #     segmentation[split] = 1

        # return segmentation


class SegmenterParams(BaseModel):
    method: str = "cvs"
    strategy: Literal["dp", "greedy"] = "dp"
    num_segments: Optional[int] = None
