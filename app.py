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

BREED_DETAILS = {
    "Gir": "Heat-tolerant dairy breed from Gujarat, known for a domed forehead and long ears.",
    "Sahiwal": "Strong milch breed with a reddish-brown coat, common in North India and Punjab regions.",
    "Rathi": "Dual-purpose cattle from Rajasthan, valued for both milk yield and hardiness.",
    "Tharparkar": "Desert-adapted breed recognized for endurance and pale grey-white coloring.",
    "Red Sindhi": "Deep reddish dairy breed suited to hot climates and low-input systems.",
    "Kankrej": "Large and powerful breed from western India, often used for both milk and draught work.",
    "Ongole": "Tall, muscular cattle breed from Andhra Pradesh with prominent hump structure.",
    "Hariana": "North Indian breed appreciated for draught strength and moderate milk production.",
    "Hallikar": "Classic southern draught breed, usually lean, agile, and energetic.",
    "Deoni": "Spotted dual-purpose cattle from the Deccan region, productive under village conditions.",
    "Murrah": "Premier Indian buffalo breed, jet black, tightly curled horns, and high milk potential.",
    "Jaffarabadi": "Heavy buffalo breed with massive body frame and drooping horns.",
    "Mehsana": "Buffalo breed from Gujarat, often selected for stable milk yield.",
    "Bhadawari": "Copper-toned buffalo known for rich-fat milk and adaptation to hot plains.",
    "Surti": "Medium-sized buffalo with sickle-shaped horns and a calm dairy temperament.",
    "Nili-Ravi": "Large river buffalo breed with a strong dairy profile and characteristic white markings.",
    "Pandharpuri": "Maharashtra buffalo breed with long sword-like horns and elongated face.",
    "Nagpuri": "Hardy buffalo breed used in dry regions, recognized for long flat horns.",
    "Toda": "Nilgiri hill buffalo associated with the Toda community and adapted to upland conditions.",
}

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


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

        :root {
            --ink: #1d2940;
            --muted: #5f6c7b;
            --sand: #f7f1e6;
            --leaf: #51643c;
            --rust: #b95c2e;
            --gold: #d7a94b;
            --panel: rgba(255, 252, 245, 0.78);
            --line: rgba(29, 41, 64, 0.08);
        }

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(215, 169, 75, 0.24), transparent 28%),
                radial-gradient(circle at left 20%, rgba(81, 100, 60, 0.18), transparent 24%),
                linear-gradient(180deg, #f4ede0 0%, #fbf8f1 45%, #f5efe4 100%);
            color: var(--ink);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero-shell {
            background: linear-gradient(135deg, rgba(255,255,255,0.84), rgba(250,240,220,0.84));
            border: 1px solid var(--line);
            border-radius: 28px;
            padding: 2rem;
            box-shadow: 0 16px 50px rgba(62, 44, 19, 0.10);
            margin-bottom: 1.4rem;
        }

        .hero-kicker {
            display: inline-block;
            font-size: 0.8rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            font-weight: 800;
            color: var(--leaf);
            background: rgba(81, 100, 60, 0.10);
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: clamp(2.3rem, 4vw, 4.2rem);
            line-height: 0.95;
            font-weight: 800;
            color: var(--ink);
            margin: 0 0 0.9rem 0;
            max-width: 9.5em;
        }

        .hero-copy {
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.7;
            max-width: 48rem;
            margin: 0;
        }

        .metric-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            min-height: 126px;
            box-shadow: 0 10px 30px rgba(29, 41, 64, 0.06);
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
        }

        .metric-value {
            color: var(--ink);
            font-size: 1.9rem;
            font-weight: 800;
            margin-top: 0.45rem;
        }

        .metric-sub {
            color: var(--muted);
            font-size: 0.92rem;
            margin-top: 0.4rem;
            line-height: 1.45;
        }

        .panel-shell {
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1.35rem;
            box-shadow: 0 10px 34px rgba(29, 41, 64, 0.06);
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--ink);
            margin-bottom: 0.2rem;
        }

        .section-copy {
            color: var(--muted);
            margin-bottom: 1rem;
            line-height: 1.6;
        }

        .result-hero {
            background: linear-gradient(135deg, rgba(81, 100, 60, 0.12), rgba(215, 169, 75, 0.18));
            border: 1px solid rgba(81, 100, 60, 0.14);
            border-radius: 22px;
            padding: 1.2rem 1.25rem;
            margin-bottom: 1rem;
        }

        .result-label {
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
        }

        .result-breed {
            color: var(--ink);
            font-size: 2rem;
            font-weight: 800;
            margin-top: 0.4rem;
        }

        .result-copy {
            color: var(--muted);
            line-height: 1.6;
            margin-top: 0.45rem;
        }

        .breed-chip {
            display: inline-block;
            margin: 0.25rem 0.35rem 0 0;
            padding: 0.45rem 0.7rem;
            border-radius: 999px;
            background: rgba(29, 41, 64, 0.06);
            color: var(--ink);
            font-size: 0.88rem;
            font-weight: 600;
        }

        .workflow-note {
            border-left: 4px solid var(--rust);
            padding: 0.85rem 1rem;
            background: rgba(185, 92, 46, 0.08);
            border-radius: 12px;
            color: var(--ink);
            margin-top: 0.75rem;
        }

        div[data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(249,243,232,0.96));
            border: 1px dashed rgba(81, 100, 60, 0.35);
            border-radius: 20px;
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--rust), #d3743d);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 0.72rem 1.1rem;
            font-weight: 800;
            box-shadow: 0 12px 25px rgba(185, 92, 46, 0.25);
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #9d4a22, #c96a32);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Indian Cattle & Buffalo Breed Recognition", layout="wide")
inject_styles()

rebuilt_index, indexed_breeds = ensure_reference_index()

if "recognizer" not in st.session_state:
    st.session_state.recognizer = BreedRecognizer(index_path=str(INDEX_PATH))
elif rebuilt_index:
    st.session_state.recognizer = BreedRecognizer(index_path=str(INDEX_PATH))

recognizer: BreedRecognizer = st.session_state.recognizer
backend_label = "Local CNN Extractor" if recognizer.backend == "offline-cnn" else "Handcrafted Offline Extractor"

st.markdown(
    """
    <div class="hero-shell">
        <div class="hero-kicker">Indian Livestock Vision</div>
        <div class="hero-title">Breed recognition for Indian cattle and buffaloes</div>
        <p class="hero-copy">
            Upload a field photo, compare it against your local breed library, and get fast offline predictions
            that are simple enough for farm teams, students, and extension workers to use.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Indexed Breeds</div>
            <div class="metric-value">{indexed_breeds}</div>
            <div class="metric-sub">The number of breed folders currently available for matching.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Recognition Mode</div>
            <div class="metric-value" style="font-size:1.35rem;">{backend_label}</div>
            <div class="metric-sub">Runs offline and keeps inference available even with unstable connectivity.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_col3:
    index_status = "Rebuilt at startup" if rebuilt_index else "Ready for prediction" if indexed_breeds > 0 else "Waiting for dataset"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Index Status</div>
            <div class="metric-value" style="font-size:1.35rem;">{index_status}</div>
            <div class="metric-sub">The app checks reference images and updates its local index automatically.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

main_col, side_col = st.columns([1.45, 0.9], gap="large")

with side_col:
    st.markdown('<div class="panel-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Supported breeds</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">The starter dataset is organized into major Indian cattle and buffalo breeds.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("".join(f'<span class="breed-chip">{breed}</span>' for breed in INDIAN_CATTLE_BREEDS), unsafe_allow_html=True)
    st.markdown("".join(f'<span class="breed-chip">{breed}</span>' for breed in INDIAN_BUFFALO_BREEDS), unsafe_allow_html=True)
    st.markdown(
        """
        <div class="workflow-note">
            Add more images inside <code>data/reference_images/&lt;breed_name&gt;/</code>.
            The app will rebuild its breed index automatically on startup.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with main_col:
    st.markdown('<div class="panel-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Upload and analyze</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Use a side-view or near-profile image with the animal clearly visible. Similar lighting and less background clutter improve matching.</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"], label_visibility="visible")
    top_k = st.slider("Number of predictions", min_value=1, max_value=5, value=3)

    if uploaded is not None:
        image = Image.open(uploaded)
        st.image(image, caption="Uploaded field image", use_container_width=True)

        if st.button("Predict Breed", type="primary"):
            with st.spinner("Analyzing image and comparing with reference breeds..."):
                predictions = recognizer.predict(image, top_k=top_k)

            if not predictions:
                st.error(
                    "No usable reference index was found. Add breed images to "
                    "`data/reference_images/<breed_name>/` and restart the app."
                )
            else:
                best = predictions[0]
                st.markdown(
                    f"""
                    <div class="result-hero">
                        <div class="result-label">Most likely match</div>
                        <div class="result-breed">{best.breed}</div>
                        <div class="result-copy">
                            Confidence: {best.confidence * 100:.1f}%<br>
                            {BREED_DETAILS.get(best.breed, "Breed summary will appear here once more metadata is added.")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                for index, pred in enumerate(predictions, start=1):
                    st.markdown(f"**{index}. {pred.breed}**")
                    st.progress(float(pred.confidence), text=f"{pred.confidence * 100:.1f}% match confidence")
                    detail = BREED_DETAILS.get(pred.breed)
                    if detail:
                        st.caption(detail)

    else:
        st.info("Upload a cattle or buffalo image to begin recognition.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="panel-shell" style="margin-top: 1.3rem;">
        <div class="section-title">Field guidance</div>
        <div class="section-copy">
            This baseline app compares images against your local breed library. It works best when each breed folder has
            multiple clear examples from similar angles. For production-grade accuracy, the next step would be training
            a dedicated classifier on a larger labeled dataset.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
