from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

from PIL import Image

from src.breed_recognition import BreedRecognizer


def collect_images(folder: Path) -> List[Path]:
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    return [p for p in folder.rglob("*") if p.suffix.lower() in exts]


def build_reference_index(reference_root: Path, output_file: Path) -> Dict[str, List[Dict[str, object]]]:
    recognizer = BreedRecognizer(index_path="models/does_not_need_to_exist.json")

    entries: List[Dict[str, object]] = []
    breed_counts: Dict[str, int] = {}

    for breed_dir in sorted([p for p in reference_root.iterdir() if p.is_dir()]):
        images = collect_images(breed_dir)
        if not images:
            continue

        valid_count = 0
        for image_path in images:
            try:
                with Image.open(image_path) as img:
                    rgb_image = img.convert("RGB")
                    vector = recognizer.extract_embedding(rgb_image)
                    image_hash = recognizer.image_hash(rgb_image)
                entries.append(
                    {
                        "breed": breed_dir.name,
                        "image_name": image_path.name,
                        "vector": vector.tolist(),
                        "image_hash": image_hash,
                    }
                )
                valid_count += 1
            except Exception:
                continue

        if valid_count > 0:
            breed_counts[breed_dir.name] = valid_count

    serializable = {
        "entries": entries,
        "breed_counts": breed_counts,
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
    print(
        f"Saved {len(index['entries'])} reference image embeddings across "
        f"{len(index['breed_counts'])} breeds to {args.output}"
    )


if __name__ == "__main__":
    main()
