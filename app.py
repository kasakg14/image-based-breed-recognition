from __future__ import annotations

from pathlib import Path

import streamlit as st
from PIL import Image

from scripts.build_index import build_reference_index, collect_images
from src.breed_recognition import BreedRecognizer


INDIAN_CATTLE_BREEDS = [
    "Gir",
    "Sahiwal",
    "Rathi",
    "Tharparkar",
    "Red Sindhi",
    "Kankrej",
    "Ongole",
    "Hariana",
    "Hallikar",
    "Deoni",
]

INDIAN_BUFFALO_BREEDS = [
    "Murrah",
    "Jaffarabadi",
    "Mehsana",
    "Bhadawari",
    "Surti",
    "Nili-Ravi",
    "Pandharpuri",
    "Nagpuri",
    "Toda",
]

REFERENCE_ROOT = Path("data/reference_images")
INDEX_PATH = Path("models/reference_index.json")


def needs_index_rebuild(reference_root: Path, index_path: Path) -> bool:
    if not index_path.exists():
        return True

    image_files = collect_images(reference_root) if reference_root.exists() else []
    if not image_files:
        return False

    latest_image_time = max(path.stat().st_mtime for path in image_files)
    return index_path.stat().st_mtime < latest_image_time


def ensure_reference_index() -> tuple[bool, int]:
    if not REFERENCE_ROOT.exists():
        return False, 0

    image_files = collect_images(REFERENCE_ROOT)
    if not image_files:
        return False, 0

    if needs_index_rebuild(REFERENCE_ROOT, INDEX_PATH):
        index = build_reference_index(REFERENCE_ROOT, INDEX_PATH)
        return True, len(index)

    recognizer = BreedRecognizer(index_path=str(INDEX_PATH))
    return False, len(recognizer.reference_vectors)


st.set_page_config(page_title="Indian Cattle & Buffalo Breed Recognition", layout="wide")

st.title("Indian Cattle & Buffalo Breed Recognition")
st.caption("Upload an animal image and get likely breed predictions.")

with st.expander("Supported target breeds"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Cattle**")
        for b in INDIAN_CATTLE_BREEDS:
            st.write(f"- {b}")
    with col2:
        st.markdown("**Buffalo**")
        for b in INDIAN_BUFFALO_BREEDS:
            st.write(f"- {b}")

rebuilt_index, indexed_breeds = ensure_reference_index()

if rebuilt_index:
    st.success(f"Reference index rebuilt automatically for {indexed_breeds} breeds.")
elif indexed_breeds > 0:
    st.info(f"Reference index ready for {indexed_breeds} breeds.")
else:
    st.info(
        "Before prediction, add reference images in `data/reference_images/<breed_name>/`. "
        "The app will build the index automatically."
    )

uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"])
top_k = st.slider("Number of predictions", min_value=1, max_value=5, value=3)

if "recognizer" not in st.session_state:
    st.session_state.recognizer = BreedRecognizer(index_path=str(INDEX_PATH))
elif rebuilt_index:
    st.session_state.recognizer = BreedRecognizer(index_path=str(INDEX_PATH))

recognizer: BreedRecognizer = st.session_state.recognizer

if recognizer.backend == "offline-cnn":
    st.success("Offline mode active: local CNN feature extractor loaded.")
else:
    st.warning("Offline mode active: using built-in handcrafted image features. No internet required.")

if uploaded is not None:
    image = Image.open(uploaded)
    st.image(image, caption="Input image", use_container_width=True)

    if st.button("Predict Breed", type="primary"):
        with st.spinner("Analyzing image..."):
            predictions = recognizer.predict(image, top_k=top_k)

        if not predictions:
            st.error(
                "Reference index not found, empty, or outdated. Rebuild it with "
                "`python -m scripts.build_index` after adding breed images."
            )
        else:
            st.subheader("Top Predictions")
            best = predictions[0]
            st.success(f"Most likely breed: **{best.breed}** ({best.confidence * 100:.1f}%)")

            for pred in predictions:
                st.write(f"{pred.breed}: {pred.confidence * 100:.1f}%")
                st.progress(float(pred.confidence))

st.markdown("---")
st.markdown(
    "Tip: Use clear side-view images, similar lighting, and rebuild the index whenever you add new breed photos."
)
