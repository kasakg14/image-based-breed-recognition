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

BREED_INSIGHTS = {
    "Gir": {
        "title": "Signature field clue",
        "trait": "Long pendulous ears with a prominent domed forehead are strong visual markers.",
        "value": "Well known for dairy strength and heat tolerance in hot regions.",
    },
    "Sahiwal": {
        "title": "Signature field clue",
        "trait": "Reddish coat tone with a deep body and calm dairy-type build.",
        "value": "One of the most respected indigenous dairy breeds in the subcontinent.",
    },
    "Rathi": {
        "title": "Signature field clue",
        "trait": "Balanced body frame suited to both milk and hardy village management.",
        "value": "Useful where farmers want a dual-purpose native breed.",
    },
    "Tharparkar": {
        "title": "Signature field clue",
        "trait": "Light grey or white body adapted to dry and desert-like conditions.",
        "value": "Recognized for endurance under scarce water and tough climates.",
    },
    "Red Sindhi": {
        "title": "Signature field clue",
        "trait": "Deep reddish coloration with a compact dairy-oriented build.",
        "value": "Performs well in hot regions and low-input systems.",
    },
    "Kankrej": {
        "title": "Signature field clue",
        "trait": "Large, powerful frame with a characteristic lyre-shaped horn profile.",
        "value": "Strong dual-purpose breed with both milk and draught importance.",
    },
    "Ongole": {
        "title": "Signature field clue",
        "trait": "Tall muscular body with a strong hump and broad stance.",
        "value": "Highly valued for strength and adaptation to tropical conditions.",
    },
    "Hariana": {
        "title": "Signature field clue",
        "trait": "Clean body lines with a practical draught-type appearance.",
        "value": "Traditionally appreciated for work capacity and moderate milk output.",
    },
    "Hallikar": {
        "title": "Signature field clue",
        "trait": "Agile lean frame with a distinctly active draught-breed look.",
        "value": "Best known historically for speed, endurance, and field work.",
    },
    "Deoni": {
        "title": "Signature field clue",
        "trait": "Often spotted or patchy coat with a sturdy dual-purpose build.",
        "value": "Performs well in village systems needing both milk and resilience.",
    },
    "Murrah": {
        "title": "Signature field clue",
        "trait": "Jet-black body with tightly curled horns is the classic Murrah marker.",
        "value": "Top Indian buffalo breed for high milk production potential.",
    },
    "Jaffarabadi": {
        "title": "Signature field clue",
        "trait": "Massive body and heavy drooping horns create a very distinct silhouette.",
        "value": "Large buffalo breed valued for strength and dairy utility.",
    },
    "Mehsana": {
        "title": "Signature field clue",
        "trait": "Medium-to-large dairy buffalo with a refined Murrah-Surti type appearance.",
        "value": "Known for stable milk yield in organized dairy systems.",
    },
    "Bhadawari": {
        "title": "Signature field clue",
        "trait": "Coppery sheen on the coat can help distinguish this breed visually.",
        "value": "Milk is often noted for comparatively rich fat content.",
    },
    "Surti": {
        "title": "Signature field clue",
        "trait": "Sickle-shaped horns and a more compact buffalo body are helpful cues.",
        "value": "A calm dairy buffalo popular in western India.",
    },
    "Nili-Ravi": {
        "title": "Signature field clue",
        "trait": "Large dairy buffalo often recognized by white markings on forehead or tail switch.",
        "value": "Strong dairy breed with a well-established milk reputation.",
    },
    "Pandharpuri": {
        "title": "Signature field clue",
        "trait": "Very long sword-like horns make this buffalo visually striking.",
        "value": "Adapted to regional conditions in Maharashtra.",
    },
    "Nagpuri": {
        "title": "Signature field clue",
        "trait": "Long flat horns and hardy frame suit drier environments.",
        "value": "Resilient breed for hot and semi-arid landscapes.",
    },
    "Toda": {
        "title": "Signature field clue",
        "trait": "Compact hill-adapted buffalo type associated with upland grazing landscapes.",
        "value": "Culturally distinctive breed tied to the Nilgiri highlands.",
    },
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
    <svg viewBox="0 0 640 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Illustration of a cow standing in an Indian farm field">
      <defs>
        <linearGradient id="sky" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="#82cfff"/>
          <stop offset="100%" stop-color="#fff6dd"/>
        </linearGradient>
        <linearGradient id="hill" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#90c56d"/>
          <stop offset="100%" stop-color="#4f9650"/>
        </linearGradient>
        <linearGradient id="field" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#d2b25f"/>
          <stop offset="100%" stop-color="#7ca348"/>
        </linearGradient>
        <linearGradient id="cowBody" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#fff7ef"/>
          <stop offset="100%" stop-color="#f1ddc8"/>
        </linearGradient>
      </defs>
      <rect width="640" height="420" rx="34" fill="url(#sky)"/>
      <circle cx="528" cy="84" r="42" fill="#ffd25e"/>
      <path d="M0 236C104 194 185 220 254 206C340 189 401 145 484 156C552 166 600 206 640 194V420H0Z" fill="url(#hill)"/>
      <path d="M0 295C88 279 144 306 230 295C305 286 360 250 428 248C511 246 568 284 640 270V420H0Z" fill="url(#field)"/>
      <path d="M0 330C81 311 145 340 210 322C278 303 334 280 420 293C508 307 566 344 640 325V420H0Z" fill="#6d9d43" opacity="0.75"/>
      <path d="M36 258L87 173L138 258Z" fill="#7b583c"/>
      <rect x="67" y="258" width="40" height="55" rx="6" fill="#b5733a"/>
      <rect x="84" y="280" width="10" height="33" fill="#5f3a25"/>
      <path d="M494 224L541 152L588 224Z" fill="#6d4d36"/>
      <rect x="523" y="224" width="35" height="44" rx="5" fill="#cf8d48"/>
      <g opacity="0.24">
        <circle cx="106" cy="66" r="18" fill="#ffffff"/>
        <circle cx="131" cy="63" r="24" fill="#ffffff"/>
        <circle cx="157" cy="68" r="17" fill="#ffffff"/>
      </g>
      <g transform="translate(150 165)">
        <ellipse cx="158" cy="120" rx="132" ry="78" fill="url(#cowBody)"/>
        <ellipse cx="259" cy="86" rx="56" ry="49" fill="url(#cowBody)"/>
        <ellipse cx="274" cy="104" rx="18" ry="14" fill="#f0b59e"/>
        <circle cx="280" cy="104" r="3.2" fill="#6f3f34"/>
        <circle cx="236" cy="82" r="5.5" fill="#182447"/>
        <path d="M248 51L276 28L271 62Z" fill="#be8750"/>
        <path d="M224 54L193 30L207 68Z" fill="#be8750"/>
        <path d="M26 118Q-5 92 13 61" stroke="#7b5b44" stroke-width="8" stroke-linecap="round" fill="none"/>
        <path d="M272 116Q308 129 324 158" stroke="#be8750" stroke-width="10" stroke-linecap="round" fill="none"/>
        <path d="M116 82C130 59 171 59 184 83C165 99 136 104 116 82Z" fill="#c98546"/>
        <path d="M172 128C187 111 223 112 233 142C212 157 184 155 172 128Z" fill="#c98546"/>
        <path d="M87 137C97 118 125 116 140 135C123 149 100 151 87 137Z" fill="#c98546"/>
        <rect x="96" y="191" width="18" height="108" rx="9" fill="#7b5b44"/>
        <rect x="158" y="193" width="18" height="106" rx="9" fill="#7b5b44"/>
        <rect x="236" y="186" width="18" height="113" rx="9" fill="#7b5b44"/>
        <rect x="286" y="182" width="18" height="117" rx="9" fill="#7b5b44"/>
        <path d="M182 160C197 149 224 150 237 167L240 193H179Z" fill="#f5dec8"/>
        <path d="M186 193H234V218C234 228 223 235 210 235C197 235 186 228 186 218Z" fill="#f0b59e"/>
      </g>
      <path d="M18 336C89 327 134 350 194 343C253 336 295 306 356 306C425 306 474 336 542 334C586 333 612 326 640 319" stroke="#87b75d" stroke-width="3" stroke-linecap="round" opacity="0.48" fill="none"/>
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

        .insight-card {
            background: linear-gradient(135deg, rgba(75, 163, 242, 0.14), rgba(244, 185, 66, 0.22), rgba(47, 125, 79, 0.14));
            border: 1px solid rgba(27, 36, 64, 0.10);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            margin: 0.85rem 0 1rem 0;
        }

        .insight-title {
            color: var(--ink);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 800;
        }

        .insight-trait {
            color: #16203b;
            font-size: 1.05rem;
            font-weight: 700;
            line-height: 1.55;
            margin-top: 0.45rem;
        }

        .insight-value {
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


st.set_page_config(page_title="पशुपहचान", layout="wide")
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
            <div class="hero-title">पशुपहचान</div>
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
                insight = BREED_INSIGHTS.get(best.breed)
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

                if insight:
                    st.markdown(
                        f"""
                        <div class="insight-card">
                            <div class="insight-title">{insight["title"]}</div>
                            <div class="insight-trait">{insight["trait"]}</div>
                            <div class="insight-value">{insight["value"]}</div>
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
