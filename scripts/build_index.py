from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
from PIL import Image

from src.breed_recognition import BreedRecognizer


def collect_images(folder: Path) -> List[Path]:
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    return [p for p in folder.rglob("*") if p.suffix.lower() in exts]


def build_reference_index(reference_root: Path, output_file: Path) -> Dict[str, List[float]]:
    recognizer = BreedRecognizer(index_path="models/does_not_need_to_exist.json")

    breed_vectors: Dict[str, np.ndarray] = {}
    for breed_dir in sorted([p for p in reference_root.iterdir() if p.is_dir()]):
        images = collect_images(breed_dir)
        if not images:
            continue

        vectors: List[np.ndarray] = []
        for image_path in images:
            try:
                with Image.open(image_path) as img:
                    vectors.append(recognizer.extract_embedding(img))
            except Exception:
                continue

        if not vectors:
            continue

        centroid = np.mean(np.stack(vectors, axis=0), axis=0)
        centroid = centroid / (np.linalg.norm(centroid) + 1e-10)
        breed_vectors[breed_dir.name] = centroid

    serializable = {
        breed: vector.astype(np.float32).tolist() for breed, vector in breed_vectors.items()
    }
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
    return serializable


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reference index for breed recognition.")
    parser.add_argument(
        "--reference-root",
        type=Path,
        default=Path("data/reference_images"),
        help="Folder containing one subfolder per breed.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("models/reference_index.json"),
        help="Where to save the generated reference index.",
    )
    args = parser.parse_args()

    if not args.reference_root.exists():
        raise FileNotFoundError(f"Reference folder not found: {args.reference_root}")

    index = build_reference_index(args.reference_root, args.output)
    print(f"Saved {len(index)} breed prototypes to {args.output}")


if __name__ == "__main__":
    main()
