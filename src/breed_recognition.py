from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
from PIL import Image, ImageFilter, ImageOps

try:
    import torch
    import torchvision.models as models
    import torchvision.transforms as transforms
except Exception:
    torch = None
    models = None
    transforms = None


@dataclass
class Prediction:
    breed: str
    confidence: float


@dataclass
class ReferenceEntry:
    breed: str
    image_name: str
    vector: np.ndarray
    image_hash: str


class BreedRecognizer:
    def __init__(self, index_path: str = "models/reference_index.json") -> None:
        self.index_path = Path(index_path)
        self.reference_entries: List[ReferenceEntry] = []
        self.backend = "offline-handcrafted"
        self.device = "cpu"
        self.model = None
        self.transform = None
        self._initialize_backend()
        self._load_index()

    def _initialize_backend(self) -> None:
        if torch is None or models is None or transforms is None:
            return

        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            model = models.efficientnet_b0(weights=None)
            model.classifier = torch.nn.Identity()
            model.eval()
            model.to(self.device)
            self.model = model
            self.transform = transforms.Compose(
                [
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225],
                    ),
                ]
            )
            self.backend = "offline-cnn"
        except Exception:
            self.backend = "offline-handcrafted"
            self.device = "cpu"
            self.model = None
            self.transform = None

    def _load_index(self) -> None:
        if not self.index_path.exists():
            self.reference_entries = []
            return

        with self.index_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        entries: List[ReferenceEntry] = []

        if isinstance(raw, dict) and "entries" in raw:
            for item in raw["entries"]:
                entries.append(
                    ReferenceEntry(
                        breed=item["breed"],
                        image_name=item.get("image_name", ""),
                        vector=np.array(item["vector"], dtype=np.float32),
                        image_hash=item.get("image_hash", ""),
                    )
                )
        else:
            for breed, vector in raw.items():
                entries.append(
                    ReferenceEntry(
                        breed=breed,
                        image_name="centroid",
                        vector=np.array(vector, dtype=np.float32),
                        image_hash="",
                    )
                )

        self.reference_entries = entries

    def is_ready(self) -> bool:
        return len(self.reference_entries) > 0

    def breed_count(self) -> int:
        return len({entry.breed for entry in self.reference_entries})

    def extract_embedding(self, image: Image.Image) -> np.ndarray:
        image = image.convert("RGB")
        if self.backend == "offline-cnn" and self.model is not None and self.transform is not None:
            tensor = self.transform(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                features = self.model(tensor).squeeze(0).detach().cpu().numpy()
            return self._normalize(features)

        return self._extract_handcrafted_features(image)

    def _extract_handcrafted_features(self, image: Image.Image) -> np.ndarray:
        resized = image.resize((192, 192))
        rgb = np.asarray(resized, dtype=np.float32) / 255.0

        hist_parts: List[np.ndarray] = []
        for channel in range(3):
            hist, _ = np.histogram(rgb[:, :, channel], bins=16, range=(0.0, 1.0))
            hist_parts.append(hist.astype(np.float32))

        gray = ImageOps.grayscale(resized)
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_array = np.asarray(edges, dtype=np.float32) / 255.0
        edge_hist, _ = np.histogram(edge_array, bins=16, range=(0.0, 1.0))

        brightness_mean = np.array([edge_array.mean()], dtype=np.float32)
        brightness_std = np.array([edge_array.std()], dtype=np.float32)

        downsample = gray.resize((16, 16))
        texture = np.asarray(downsample, dtype=np.float32).flatten() / 255.0

        features = np.concatenate(
            hist_parts
            + [
                edge_hist.astype(np.float32),
                brightness_mean,
                brightness_std,
                texture.astype(np.float32),
            ]
        )
        return self._normalize(features)

    @staticmethod
    def image_hash(image: Image.Image, size: int = 8) -> str:
        grayscale = ImageOps.grayscale(image.convert("RGB")).resize((size, size))
        pixels = np.asarray(grayscale, dtype=np.float32)
        threshold = float(pixels.mean())
        bits = ["1" if value >= threshold else "0" for value in pixels.flatten()]
        return "".join(bits)

    @staticmethod
    def hamming_distance(hash_a: str, hash_b: str) -> int:
        if not hash_a or not hash_b or len(hash_a) != len(hash_b):
            return 999
        return sum(bit_a != bit_b for bit_a, bit_b in zip(hash_a, hash_b))

    @staticmethod
    def _normalize(vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector) + 1e-10
        return vector / norm

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / ((np.linalg.norm(a) + 1e-10) * (np.linalg.norm(b) + 1e-10)))

    def predict(self, image: Image.Image, top_k: int = 3, vote_k: int = 7) -> List[Prediction]:
        if not self.is_ready():
            return []

        query_hash = self.image_hash(image)
        closest_reference = min(
            self.reference_entries,
            key=lambda entry: self.hamming_distance(query_hash, entry.image_hash),
            default=None,
        )
        if closest_reference is not None:
            hash_distance = self.hamming_distance(query_hash, closest_reference.image_hash)
            if hash_distance <= 2:
                return [Prediction(breed=closest_reference.breed, confidence=0.99)]

        query_embedding = self.extract_embedding(image)
        image_matches: List[tuple[str, float]] = []

        for entry in self.reference_entries:
            if entry.vector.shape != query_embedding.shape:
                continue
            sim = self._cosine_similarity(query_embedding, entry.vector)
            image_matches.append((entry.breed, sim))

        if not image_matches:
            return []

        image_matches.sort(key=lambda item: item[1], reverse=True)
        nearest = image_matches[: min(vote_k, len(image_matches))]

        breed_scores: Dict[str, List[float]] = {}
        for breed, similarity in nearest:
            breed_scores.setdefault(breed, []).append(similarity)

        scores: List[Prediction] = []
        for breed, similarities in breed_scores.items():
            weighted_similarity = float(np.mean(similarities) + 0.05 * (len(similarities) - 1))
            conf = max(0.0, min(1.0, (weighted_similarity + 1.0) / 2.0))
            scores.append(Prediction(breed=breed, confidence=conf))

        scores.sort(key=lambda item: item.confidence, reverse=True)
        return scores[:top_k]
