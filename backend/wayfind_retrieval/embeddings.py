"""Text embedders.

``minilm`` is the real model: all-MiniLM-L6-v2 run through ONNX Runtime (Chroma's built-in
copy), so no PyTorch and no API key are needed. ``hashing`` is a deterministic bag-of-words
embedder used by unit tests and offline CI; it is not a retrieval model.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

TOKEN = re.compile(r"[a-z0-9]+")


class Embedder(Protocol):
    name: str

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class MiniLMEmbedder:
    name = "all-MiniLM-L6-v2 (onnx)"

    def __init__(self) -> None:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        self._model = ONNXMiniLM_L6_V2()

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(value) for value in vector] for vector in self._model(texts)]


class HashingEmbedder:
    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions
        self.name = f"hashing-{dimensions}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in TOKEN.findall(text.lower()):
            digest = hashlib.md5(token.encode()).digest()
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[int.from_bytes(digest[:4], "big") % self.dimensions] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


def make_embedder(name: str) -> Embedder:
    if name == "minilm":
        return MiniLMEmbedder()
    if name == "hashing":
        return HashingEmbedder()
    raise ValueError(f"Unknown embedder {name!r}; use 'minilm' or 'hashing'")
