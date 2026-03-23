from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms


VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass
class TrainingConfig:
    data_root: str
    output_dir: str
    epochs: int
    batch_size: int
    learning_rate: float
    train_split: float
    image_size: int
    seed: int


class BreedImageDataset(Dataset):
    def __init__(
        self,
        samples: Sequence[Tuple[Path, int]],
        transform: transforms.Compose,
    ) -> None:
        self.samples = list(samples)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int]:
        image_path, label = self.samples[index]
        with Image.open(image_path) as image:
            tensor = self.transform(image.convert("RGB"))
        return tensor, label


def collect_samples(data_root: Path) -> Tuple[List[Tuple[Path, int]], Dict[int, str]]:
    breed_dirs = sorted([path for path in data_root.iterdir() if path.is_dir()])
    label_to_breed: Dict[int, str] = {}
    samples: List[Tuple[Path, int]] = []

    for label, breed_dir in enumerate(breed_dirs):
        label_to_breed[label] = breed_dir.name
        for image_path in breed_dir.rglob("*"):
            if image_path.suffix.lower() in VALID_EXTENSIONS:
                samples.append((image_path, label))

    return samples, label_to_breed


def split_samples(
    samples: Sequence[Tuple[Path, int]],
    train_split: float,
    seed: int,
) -> Tuple[List[Tuple[Path, int]], List[Tuple[Path, int]]]:
    grouped: Dict[int, List[Tuple[Path, int]]] = {}
    for sample in samples:
        grouped.setdefault(sample[1], []).append(sample)

    train_samples: List[Tuple[Path, int]] = []
    val_samples: List[Tuple[Path, int]] = []
    rng = random.Random(seed)

    for label_samples in grouped.values():
        shuffled = list(label_samples)
        rng.shuffle(shuffled)
        split_index = max(1, int(len(shuffled) * train_split))
        if split_index >= len(shuffled):
            split_index = len(shuffled) - 1
        train_samples.extend(shuffled[:split_index])
        val_samples.extend(shuffled[split_index:])

    return train_samples, val_samples


def build_transforms(image_size: int) -> Tuple[transforms.Compose, transforms.Compose]:
    train_transform = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    val_transform = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    return train_transform, val_transform


def create_model(num_classes: int) -> nn.Module:
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


def evaluate(model: nn.Module, dataloader: DataLoader, criterion: nn.Module, device: str) -> Tuple[float, float]:
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * inputs.size(0)
            predictions = outputs.argmax(dim=1)
            correct += int((predictions == labels).sum().item())
            total += labels.size(0)

    avg_loss = total_loss / max(total, 1)
    accuracy = correct / max(total, 1)
    return avg_loss, accuracy


def train(config: TrainingConfig) -> None:
    torch.manual_seed(config.seed)
    random.seed(config.seed)

    data_root = Path(config.data_root)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    samples, label_to_breed = collect_samples(data_root)
    if not samples:
        raise ValueError("No training images found in the dataset folders.")

    train_samples, val_samples = split_samples(samples, config.train_split, config.seed)
    if not train_samples or not val_samples:
        raise ValueError("Need at least two images per breed to create training and validation splits.")

    train_transform, val_transform = build_transforms(config.image_size)

    train_dataset = BreedImageDataset(train_samples, train_transform)
    val_dataset = BreedImageDataset(val_samples, val_transform)

    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = create_model(num_classes=len(label_to_breed)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)

    best_accuracy = 0.0
    history: List[Dict[str, float]] = []

    for epoch in range(1, config.epochs + 1):
        model.train()
        running_loss = 0.0
        running_correct = 0
        running_total = 0

        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            predictions = outputs.argmax(dim=1)
            running_correct += int((predictions == labels).sum().item())
            running_total += labels.size(0)

        train_loss = running_loss / max(running_total, 1)
        train_accuracy = running_correct / max(running_total, 1)
        val_loss, val_accuracy = evaluate(model, val_loader, criterion, device)

        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "train_accuracy": train_accuracy,
                "val_loss": val_loss,
                "val_accuracy": val_accuracy,
            }
        )

        print(
            f"Epoch {epoch}/{config.epochs} | "
            f"train_loss={train_loss:.4f} train_acc={train_accuracy:.4f} | "
            f"val_loss={val_loss:.4f} val_acc={val_accuracy:.4f}"
        )

        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "label_to_breed": label_to_breed,
                    "image_size": config.image_size,
                },
                output_dir / "best_model.pt",
            )

    metadata = {
        "config": asdict(config),
        "label_to_breed": label_to_breed,
        "history": history,
        "best_val_accuracy": best_accuracy,
    }
    with (output_dir / "training_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved best model and metadata to {output_dir}")


def parse_args() -> TrainingConfig:
    parser = argparse.ArgumentParser(description="Train a cattle/buffalo breed classifier.")
    parser.add_argument("--data-root", type=str, default="data/reference_images")
    parser.add_argument("--output-dir", type=str, default="models/classifier")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=0.0003)
    parser.add_argument("--train-split", type=float, default=0.8)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    return TrainingConfig(
        data_root=args.data_root,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        train_split=args.train_split,
        image_size=args.image_size,
        seed=args.seed,
    )


if __name__ == "__main__":
    train(parse_args())
