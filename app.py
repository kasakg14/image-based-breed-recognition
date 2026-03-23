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


def render_hero_art() -> str:
    return """
    <svg viewBox="0 0 640 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Illustration of Indian cattle and buffalo landscape">
      <defs>
        <linearGradient id="sky" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="#8fd0ff"/>
          <stop offset="100%" stop-color="#fff7e0"/>
        </linearGradient>
        <linearGradient id="ground" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#7fbf6e"/>
          <stop offset="100%" stop-color="#d7a14a"/>
        </linearGradient>
      </defs>
      <rect width="640" height="420" rx="34" fill="url(#sky)"/>
      <circle cx="535" cy="88" r="46" fill="#ffd15c" opacity="0.95"/>
      <path d="M0 255C119 219 168 272 251 261C352 248 390 185 485 201C545 211 595 245 640 231V420H0Z" fill="url(#ground)"/>
      <path d="M0 302C119 286 208 332 296 310C377 289 455 257 558 290C585 299 611 310 640 303V420H0Z" fill="#5a9850" opacity="0.65"/>
      <g transform="translate(78 153)">
        <ellipse cx="132" cy="123" rx="106" ry="66" fill="#f4f0e6"/>
        <ellipse cx="214" cy="94" rx="49" ry="42" fill="#f4f0e6"/>
        <path d="M220 70L249 45L242 82Z" fill="#cf7b4b"/>
        <path d="M192 70L161 42L172 83Z" fill="#cf7b4b"/>
        <circle cx="225" cy="92" r="5.5" fill="#1d2940"/>
        <path d="M251 109Q274 115 288 139" stroke="#cf7b4b" stroke-width="9" stroke-linecap="round" fill="none"/>
        <rect x="82" y="173" width="16" height="98" rx="8" fill="#76513b"/>
        <rect x="142" y="173" width="16" height="98" rx="8" fill="#76513b"/>
        <rect x="208" y="168" width="16" height="103" rx="8" fill="#76513b"/>
        <rect x="254" y="165" width="16" height="106" rx="8" fill="#76513b"/>
        <path d="M52 126Q31 89 9 99" stroke="#76513b" stroke-width="8" stroke-linecap="round" fill="none"/>
      </g>
      <g transform="translate(336 186)">
        <ellipse cx="110" cy="103" rx="92" ry="59" fill="#2b324b"/>
        <ellipse cx="183" cy="86" rx="45" ry="39" fill="#2b324b"/>
        <path d="M153 69Q128 34 97 31" stroke="#2b324b" stroke-width="12" stroke-linecap="round" fill="none"/>
        <path d="M211 66Q242 21 281 30" stroke="#2b324b" stroke-width="12" stroke-linecap="round" fill="none"/>
        <circle cx="192" cy="85" r="5.5" fill="#f5f1e8"/>
        <rect x="66" y="154" width="15" height="90" rx="7" fill="#1d2235"/>
        <rect x="119" y="154" width="15" height="90" rx="7" fill="#1d2235"/>
        <rect x="167" y="149" width="15" height="95" rx="7" fill="#1d2235"/>
        <rect x="210" y="150" width="15" height="94" rx="7" fill="#1d2235"/>
      </g>
      <g opacity="0.25">
        <circle cx="95" cy="66" r="18" fill="#ffffff"/>
        <circle cx="122" cy="66" r="22" fill="#ffffff"/>
        <circle cx="145" cy="70" r="16" fill="#ffffff"/>
      </g>
    </svg>
    """


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

        :root {
            --ink: #1b2440;
            --muted: #5d6486;
            --sand: #fff5dd;
            --leaf: #2f7d4f;
            --rust: #ef6a3c;
            --gold: #f4b942;
            --berry: #d94f70;
            --sky: #4ba3f2;
            --panel: rgba(255, 252, 245, 0.82);
            --line: rgba(27, 36, 64, 0.09);
        }

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(244, 185, 66, 0.30), transparent 26%),
                radial-gradient(circle at left 18%, rgba(75, 163, 242, 0.18), transparent 24%),
                radial-gradient(circle at bottom right, rgba(217, 79, 112, 0.16), transparent 22%),
                linear-gradient(180deg, #fff7e7 0%, #fffdf7 46%, #f8f0ff 100%);
            color: var(--ink);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero-shell {
            background:
                linear-gradient(135deg, rgba(255,255,255,0.90), rgba(255,243,211,0.88)),
                linear-gradient(120deg, rgba(75,163,242,0.08), rgba(217,79,112,0.08));
            border: 1px solid var(--line);
            border-radius: 28px;
            padding: 2rem;
            box-shadow: 0 18px 60px rgba(77, 63, 33, 0.14);
            margin-bottom: 1.4rem;
        }

        .hero-kicker {
            display: inline-block;
            font-size: 0.8rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            font-weight: 800;
            color: var(--leaf);
            background: linear-gradient(135deg, rgba(47, 125, 79, 0.14), rgba(75, 163, 242, 0.12));
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: clamp(2.3rem, 4vw, 4.2rem);
            line-height: 0.95;
            font-weight: 800;
            color: #17213d;
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

        .hero-art-shell {
            background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,244,224,0.90));
            border: 1px solid var(--line);
            border-radius: 28px;
            padding: 0.7rem;
            box-shadow: 0 18px 46px rgba(29, 41, 64, 0.12);
            height: 100%;
        }

        .hero-art-shell svg {
            width: 100%;
            height: auto;
            display: block;
            border-radius: 22px;
        }

        .metric-card {
            background:
                linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,247,231,0.88));
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            min-height: 126px;
            box-shadow: 0 12px 36px rgba(29, 41, 64, 0.08);
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
        }

        .metric-value {
            color: #182447;
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
            background:
                linear-gradient(180deg, rgba(255,255,255,0.86), rgba(255,250,240,0.82));
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1.35rem;
            box-shadow: 0 12px 34px rgba(29, 41, 64, 0.08);
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
            background:
                linear-gradient(135deg, rgba(47, 125, 79, 0.15), rgba(244, 185, 66, 0.24), rgba(75, 163, 242, 0.14));
            border: 1px solid rgba(47, 125, 79, 0.16);
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
            color: #16203b;
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
            background: linear-gradient(135deg, rgba(75, 163, 242, 0.14), rgba(217, 79, 112, 0.14));
            color: var(--ink);
            font-size: 0.88rem;
            font-weight: 600;
        }

        .workflow-note {
            border-left: 4px solid var(--rust);
            padding: 0.85rem 1rem;
            background: linear-gradient(135deg, rgba(239, 106, 60, 0.10), rgba(244, 185, 66, 0.12));
            border-radius: 12px;
            color: var(--ink);
            margin-top: 0.75rem;
        }

        div[data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(243,249,255,0.95));
            border: 1px dashed rgba(75, 163, 242, 0.42);
            border-radius: 20px;
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--rust), var(--berry), var(--gold));
            color: white;
            border: none;
            border-radius: 14px;
            padding: 0.72rem 1.1rem;
            font-weight: 800;
            box-shadow: 0 14px 28px rgba(217, 79, 112, 0.24);
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #d75629, #c73f61, #e2a22d);
        }

        div[data-testid="stProgressBar"] > div > div > div {
            background: linear-gradient(90deg, var(--leaf), var(--sky), var(--gold));
        }

        div[data-testid="stAlert"] {
            border-radius: 18px;
            border: 1px solid rgba(27, 36, 64, 0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="PASHUPAHECHAN", layout="wide")
inject_styles()

rebuilt_index, indexed_breeds = ensure_reference_index()

if "recognizer" not in st.session_state:
    st.session_state.recognizer = BreedRecognizer(index_path=str(INDEX_PATH))
elif rebuilt_index:
    st.session_state.recognizer = BreedRecognizer(index_path=str(INDEX_PATH))

recognizer: BreedRecognizer = st.session_state.recognizer
backend_label = "Local CNN Extractor" if recognizer.backend == "offline-cnn" else "Handcrafted Offline Extractor"

hero_col, art_col = st.columns([1.2, 0.95], gap="large")
with hero_col:
    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-kicker">Indian Livestock Vision</div>
            <div class="hero-title">PASHUPAHECHAN</div>
            <p class="hero-copy">
                Breed recognition for Indian cattle and buffaloes with fast offline predictions for field teams,
                students, and livestock extension workers.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with art_col:
    st.markdown(f'<div class="hero-art-shell">{render_hero_art()}</div>', unsafe_allow_html=True)

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
