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


class BreedRecognizer:
    def __init__(self, index_path: str = "models/reference_index.json") -> None:
        self.index_path = Path(index_path)
        self.reference_vectors: Dict[str, np.ndarray] = {}
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
            self.reference_vectors = {}
            return

        with self.index_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        self.reference_vectors = {
            breed: np.array(vector, dtype=np.float32) for breed, vector in raw.items()
        }

    def is_ready(self) -> bool:
        return len(self.reference_vectors) > 0

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
    def _normalize(vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector) + 1e-10
        return vector / norm

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / ((np.linalg.norm(a) + 1e-10) * (np.linalg.norm(b) + 1e-10)))

    def predict(self, image: Image.Image, top_k: int = 3) -> List[Prediction]:
        if not self.is_ready():
            return []

        query_embedding = self.extract_embedding(image)
        scores: List[Prediction] = []
        for breed, ref_vector in self.reference_vectors.items():
            if ref_vector.shape != query_embedding.shape:
                continue
            sim = self._cosine_similarity(query_embedding, ref_vector)
            conf = max(0.0, min(1.0, (sim + 1.0) / 2.0))
            scores.append(Prediction(breed=breed, confidence=conf))

        scores.sort(key=lambda x: x.confidence, reverse=True)
        return scores[:top_k]
