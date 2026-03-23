from __future__ import annotations

import streamlit as st
from PIL import Image

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

st.info(
    "Before prediction, add reference images in `data/reference_images/<breed_name>/` "
    "and run: `python -m scripts.build_index`"
)

uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"])
top_k = st.slider("Number of predictions", min_value=1, max_value=5, value=3)

if "recognizer" not in st.session_state:
    st.session_state.recognizer = BreedRecognizer()

recognizer: BreedRecognizer = st.session_state.recognizer

if recognizer.backend == "offline-cnn":
    st.success("Offline mode active: local CNN feature extractor loaded.")
else:
    st.warning("Offline mode active: using built-in handcrafted image features. No internet required.")

if uploaded is not None:
    image = Image.open(uploaded)
    st.image(image, caption="Input image", width="stretch")

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
