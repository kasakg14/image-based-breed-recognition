# Indian Cattle & Buffalo Breed Recognition App

This is a Streamlit app for image-based breed recognition of Indian cattle and buffaloes.
It now supports a fully offline workflow.

## How It Works

- You provide a small labeled reference set of breed images.
- The app extracts visual features locally on your machine.
- If Torch is available locally, it uses an offline CNN feature extractor.
- If Torch is unavailable or fails, it falls back to a built-in handcrafted feature extractor.
- For each breed, it builds a prototype vector (average embedding).
- Uploaded images are matched by cosine similarity against breed prototypes.

## Project Structure

- `app.py`: Streamlit UI
- `src/breed_recognition.py`: Recognition engine
- `scripts/build_index.py`: Build reference index from images
- `data/reference_images/`: Put breed-wise folders and images here
- `models/reference_index.json`: Generated index file

## Quick Start

1. Create and activate virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add reference images:

```text
data/reference_images/
  Gir/
    img1.jpg
    img2.jpg
  Sahiwal/
    img1.jpg
  Murrah/
    img1.jpg
```

4. Build the index:

```bash
python -m scripts.build_index
```

5. Run the app:

```bash
streamlit run app.py
```

## Offline Use

- No internet is required to run predictions once dependencies are installed.
- Add breed images into `data/reference_images/<breed_name>/`.
- The app can auto-build the index on startup when deployed.
- For local development, you can still rebuild manually after adding or changing dataset images:

```bash
python -m scripts.build_index
```

## Notes

- Prediction quality depends heavily on reference image quality and diversity.
- The handcrafted offline mode is lightweight and reliable, but usually less accurate than a trained classifier.
- This is a baseline similarity system, not a fully supervised production classifier.

## Training A Real Classifier

To improve accuracy beyond similarity matching, train a supervised model:

```bash
python -m scripts.train_classifier --data-root data/reference_images --output-dir models/classifier
```

This saves:

- `models/classifier/best_model.pt`
- `models/classifier/training_metadata.json`

Recommended dataset quality:

- 50+ images per breed if possible
- similar framing and side views
- correctly labeled breed folders
- balanced image counts across breeds
