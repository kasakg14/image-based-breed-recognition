from __future__ import annotations

from pathlib import Path

import streamlit as st
from PIL import Image

from scripts.build_index import build_reference_index, collect_images
from src.breed_recognition import BreedRecognizer


LANGUAGE_OPTIONS = {
    "English": "en",
    "हिंदी": "hi",
    "मराठी": "mr",
}

TEXT = {
    "en": {
        "page_title": "PASHUPAHECHAN",
        "lang": "Language",
        "hero_kicker": "Indian Livestock Vision",
        "hero_title": "पशुपहचान",
        "hero_copy": "Breed recognition for Indian cattle and buffaloes with fast offline predictions for field teams, students, and livestock extension workers.",
        "indexed_breeds": "Indexed Breeds",
        "indexed_breeds_sub": "Breed folders currently ready for matching.",
        "recognition_mode": "Recognition Mode",
        "recognition_mode_sub": "Runs offline and remains usable even with poor connectivity.",
        "index_status": "Index Status",
        "index_status_sub": "Reference images are checked and indexed automatically.",
        "rebuilt": "Rebuilt at startup",
        "ready": "Ready for prediction",
        "waiting": "Waiting for dataset",
        "supported": "Supported breeds",
        "supported_copy": "Starter support includes major Indian cattle and buffalo breeds.",
        "workflow_note": "Add more images in data/reference_images/<breed_name>/. The app rebuilds its breed index automatically on startup.",
        "upload_title": "Upload and analyze",
        "upload_copy": "Use a clear side-view or near-profile animal image. Similar lighting and less background clutter improve matching.",
        "upload_label": "Upload image",
        "prediction_count": "Number of predictions",
        "upload_caption": "Uploaded field image",
        "predict": "Predict Breed",
        "spinner": "Analyzing image and comparing with reference breeds...",
        "no_index": "No usable reference index was found. Add breed images to data/reference_images/<breed_name>/ and restart the app.",
        "most_likely": "Most likely match",
        "confidence": "Confidence",
        "match_confidence": "match confidence",
        "insight_title": "Signature field clue",
        "upload_prompt": "Upload a cattle or buffalo image to begin recognition.",
        "field_guidance": "Field guidance",
        "field_guidance_copy": "This baseline app compares images against your local breed library. It works best when each breed folder has multiple clear examples from similar angles. For higher accuracy, the next step would be training a dedicated classifier on a larger labeled dataset.",
        "offline_cnn": "Offline mode active: local CNN feature extractor loaded.",
        "offline_hand": "Offline mode active: built-in handcrafted image features loaded. No internet required.",
        "backend_cnn": "Local CNN Extractor",
        "backend_hand": "Handcrafted Offline Extractor",
        "breed_fallback": "More breed information can be added here.",
    },
    "hi": {
        "page_title": "पशुपहचान",
        "lang": "भाषा",
        "hero_kicker": "भारतीय पशुधन दृष्टि",
        "hero_title": "पशुपहचान",
        "hero_copy": "भारतीय गायों और भैंसों की नस्ल पहचान के लिए तेज ऑफलाइन अनुमान, जो फील्ड टीम, छात्रों और पशुपालन कार्यकर्ताओं के लिए उपयोगी है।",
        "indexed_breeds": "सूचीबद्ध नस्लें",
        "indexed_breeds_sub": "मिलान के लिए उपलब्ध नस्ल फ़ोल्डर।",
        "recognition_mode": "पहचान मोड",
        "recognition_mode_sub": "यह ऑफलाइन चलता है और कमजोर नेटवर्क में भी उपयोगी रहता है।",
        "index_status": "इंडेक्स स्थिति",
        "index_status_sub": "रेफरेंस इमेज अपने-आप जांची और इंडेक्स की जाती हैं।",
        "rebuilt": "शुरू होते समय फिर से बनाया गया",
        "ready": "पहचान के लिए तैयार",
        "waiting": "डेटासेट की प्रतीक्षा",
        "supported": "समर्थित नस्लें",
        "supported_copy": "शुरुआती समर्थन में प्रमुख भारतीय गाय और भैंस नस्लें शामिल हैं।",
        "workflow_note": "data/reference_images/<breed_name>/ में और तस्वीरें जोड़ें। ऐप शुरू होते ही इंडेक्स अपने-आप बना देगा।",
        "upload_title": "तस्वीर अपलोड करें और जांचें",
        "upload_copy": "जानवर की साफ साइड या प्रोफाइल फोटो दें। समान रोशनी और कम पृष्ठभूमि शोर से परिणाम बेहतर मिलते हैं।",
        "upload_label": "तस्वीर अपलोड करें",
        "prediction_count": "कितनी भविष्यवाणियां दिखानी हैं",
        "upload_caption": "अपलोड की गई तस्वीर",
        "predict": "नस्ल पहचानें",
        "spinner": "तस्वीर का विश्लेषण किया जा रहा है और रेफरेंस नस्लों से तुलना हो रही है...",
        "no_index": "उपयोग योग्य रेफरेंस इंडेक्स नहीं मिला। data/reference_images/<breed_name>/ में नस्ल की तस्वीरें जोड़ें और ऐप फिर से शुरू करें।",
        "most_likely": "सबसे संभावित मिलान",
        "confidence": "विश्वास स्तर",
        "match_confidence": "मिलान विश्वास स्तर",
        "insight_title": "मैदान में पहचान का संकेत",
        "upload_prompt": "पहचान शुरू करने के लिए गाय या भैंस की तस्वीर अपलोड करें।",
        "field_guidance": "मैदानी सुझाव",
        "field_guidance_copy": "यह प्रारंभिक ऐप आपकी स्थानीय नस्ल लाइब्रेरी से तुलना करता है। बेहतर परिणाम के लिए हर नस्ल फ़ोल्डर में एक जैसे कोणों से कई साफ तस्वीरें रखें। अधिक सटीकता के लिए आगे चलकर बड़े लेबल्ड डेटासेट पर अलग मॉडल प्रशिक्षित किया जा सकता है।",
        "offline_cnn": "ऑफलाइन मोड सक्रिय है: लोकल CNN फीचर एक्सट्रैक्टर लोड हो गया है।",
        "offline_hand": "ऑफलाइन मोड सक्रिय है: बिल्ट-इन हैंडक्राफ्टेड इमेज फीचर उपयोग हो रहे हैं। इंटरनेट की जरूरत नहीं है।",
        "backend_cnn": "लोकल CNN एक्सट्रैक्टर",
        "backend_hand": "हैंडक्राफ्टेड ऑफलाइन एक्सट्रैक्टर",
        "breed_fallback": "यहां बाद में और नस्ल जानकारी जोड़ी जा सकती है।",
    },
    "mr": {
        "page_title": "पशुपहचान",
        "lang": "भाषा",
        "hero_kicker": "भारतीय पशुधन दृष्टी",
        "hero_title": "पशुपहचान",
        "hero_copy": "भारतीय गायी आणि म्हशींच्या जाती ओळखण्यासाठी जलद ऑफलाइन अंदाज, जे शेतकरी, विद्यार्थी आणि पशुपालन कार्यकर्त्यांसाठी उपयुक्त आहे.",
        "indexed_breeds": "नोंदलेल्या जाती",
        "indexed_breeds_sub": "तुलनेसाठी उपलब्ध जातींचे फोल्डर.",
        "recognition_mode": "ओळख मोड",
        "recognition_mode_sub": "हे अॅप ऑफलाइन चालते आणि कमी नेटवर्कमध्येही उपयोगी राहते.",
        "index_status": "इंडेक्स स्थिती",
        "index_status_sub": "रेफरन्स फोटो आपोआप तपासले जातात आणि इंडेक्स तयार होतो.",
        "rebuilt": "सुरुवातीला पुन्हा तयार",
        "ready": "अंदाजासाठी तयार",
        "waiting": "डेटासेटची वाट पाहत आहे",
        "supported": "समर्थित जाती",
        "supported_copy": "प्राथमिक समर्थनात प्रमुख भारतीय गायी आणि म्हशींच्या जाती आहेत.",
        "workflow_note": "data/reference_images/<breed_name>/ मध्ये अधिक फोटो जोडा. अॅप सुरू होताच इंडेक्स आपोआप तयार होईल.",
        "upload_title": "फोटो अपलोड करा आणि तपासा",
        "upload_copy": "प्राण्याचा स्पष्ट बाजूचा किंवा प्रोफाइल फोटो वापरा. सारखी प्रकाशव्यवस्था आणि कमी पार्श्वभूमी गोंधळ यामुळे परिणाम सुधारतात.",
        "upload_label": "फोटो अपलोड करा",
        "prediction_count": "किती अंदाज दाखवायचे",
        "upload_caption": "अपलोड केलेला फोटो",
        "predict": "जात ओळखा",
        "spinner": "फोटोचे विश्लेषण करून रेफरन्स जातींशी तुलना केली जात आहे...",
        "no_index": "उपयोगी रेफरन्स इंडेक्स सापडला नाही. data/reference_images/<breed_name>/ मध्ये जातीचे फोटो जोडा आणि अॅप पुन्हा सुरू करा.",
        "most_likely": "सर्वात संभाव्य जुळणी",
        "confidence": "विश्वास पातळी",
        "match_confidence": "जुळणी विश्वास पातळी",
        "insight_title": "मैदानी ओळखीचा संकेत",
        "upload_prompt": "ओळख सुरू करण्यासाठी गाय किंवा म्हशीचा फोटो अपलोड करा.",
        "field_guidance": "मैदानी मार्गदर्शन",
        "field_guidance_copy": "हे प्राथमिक अॅप तुमच्या स्थानिक जातींच्या लायब्ररीशी तुलना करते. चांगल्या परिणामांसाठी प्रत्येक जातीच्या फोल्डरमध्ये एकसारख्या कोनातील अनेक स्पष्ट फोटो ठेवा. अधिक अचूकतेसाठी पुढील टप्प्यात मोठ्या लेबल्ड डेटासेटवर स्वतंत्र मॉडेल प्रशिक्षित करता येईल.",
        "offline_cnn": "ऑफलाइन मोड सक्रिय: लोकल CNN फीचर एक्स्ट्रॅक्टर लोड झाला आहे.",
        "offline_hand": "ऑफलाइन मोड सक्रिय: अंगभूत हँडक्राफ्टेड इमेज फीचर्स वापरले जात आहेत. इंटरनेटची गरज नाही.",
        "backend_cnn": "लोकल CNN एक्स्ट्रॅक्टर",
        "backend_hand": "हँडक्राफ्टेड ऑफलाइन एक्स्ट्रॅक्टर",
        "breed_fallback": "येथे पुढे अधिक जातीची माहिती जोडता येईल.",
    },
}

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
        "trait": "Long pendulous ears with a prominent domed forehead are strong visual markers.",
        "value": "Well known for dairy strength and heat tolerance in hot regions.",
    },
    "Sahiwal": {
        "trait": "Reddish coat tone with a deep body and calm dairy-type build.",
        "value": "One of the most respected indigenous dairy breeds in the subcontinent.",
    },
    "Murrah": {
        "trait": "Jet-black body with tightly curled horns is the classic Murrah marker.",
        "value": "Top Indian buffalo breed for high milk production potential.",
    },
    "Kankrej": {
        "trait": "Large, powerful frame with a characteristic lyre-shaped horn profile.",
        "value": "Strong dual-purpose breed with both milk and draught importance.",
    },
    "Pandharpuri": {
        "trait": "Very long sword-like horns make this buffalo visually striking.",
        "value": "Adapted to regional conditions in Maharashtra.",
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
    <svg viewBox="0 0 640 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cow standing in an Indian farm field">
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
      <g transform="translate(150 165)">
        <ellipse cx="158" cy="120" rx="132" ry="78" fill="url(#cowBody)"/>
        <ellipse cx="259" cy="86" rx="56" ry="49" fill="url(#cowBody)"/>
        <path d="M248 51L276 28L271 62Z" fill="#be8750"/>
        <path d="M224 54L193 30L207 68Z" fill="#be8750"/>
        <circle cx="236" cy="82" r="5.5" fill="#182447"/>
        <path d="M116 82C130 59 171 59 184 83C165 99 136 104 116 82Z" fill="#c98546"/>
        <path d="M172 128C187 111 223 112 233 142C212 157 184 155 172 128Z" fill="#c98546"/>
        <path d="M87 137C97 118 125 116 140 135C123 149 100 151 87 137Z" fill="#c98546"/>
        <rect x="96" y="191" width="18" height="108" rx="9" fill="#7b5b44"/>
        <rect x="158" y="193" width="18" height="106" rx="9" fill="#7b5b44"/>
        <rect x="236" y="186" width="18" height="113" rx="9" fill="#7b5b44"/>
        <rect x="286" y="182" width="18" height="117" rx="9" fill="#7b5b44"/>
      </g>
    </svg>
    """


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(244, 185, 66, 0.30), transparent 26%),
                radial-gradient(circle at left 18%, rgba(75, 163, 242, 0.18), transparent 24%),
                radial-gradient(circle at bottom right, rgba(217, 79, 112, 0.16), transparent 22%),
                linear-gradient(180deg, #fff7e7 0%, #fffdf7 46%, #f8f0ff 100%);
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        .hero-shell, .panel-shell, .metric-card, .hero-art-shell, .result-hero, .insight-card {
            border-radius: 24px;
            border: 1px solid rgba(27, 36, 64, 0.09);
            box-shadow: 0 12px 32px rgba(29, 41, 64, 0.08);
        }
        .hero-shell, .panel-shell, .metric-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,248,236,0.86));
            padding: 1.3rem;
        }
        .hero-art-shell {
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,248,236,0.90));
            padding: 0.7rem;
        }
        .hero-kicker {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(47,125,79,0.14), rgba(75,163,242,0.12));
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #2f7d4f;
        }
        .hero-title {
            font-size: clamp(2.2rem, 4vw, 4rem);
            font-weight: 800;
            color: #17213d;
            margin: 0.8rem 0;
        }
        .hero-copy, .section-copy, .metric-sub, .result-copy, .insight-value {
            color: #5d6486;
            line-height: 1.6;
        }
        .metric-label, .result-label, .insight-title {
            color: #5d6486;
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
        }
        .metric-value, .result-breed {
            color: #182447;
            font-weight: 800;
        }
        .metric-value {
            font-size: 1.7rem;
            margin-top: 0.35rem;
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 800;
            color: #1b2440;
        }
        .breed-chip {
            display: inline-block;
            margin: 0.25rem 0.35rem 0 0;
            padding: 0.45rem 0.7rem;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(75,163,242,0.14), rgba(217,79,112,0.14));
            color: #1b2440;
            font-size: 0.88rem;
            font-weight: 600;
        }
        .workflow-note {
            margin-top: 0.8rem;
            padding: 0.85rem 1rem;
            border-left: 4px solid #ef6a3c;
            background: linear-gradient(135deg, rgba(239,106,60,0.10), rgba(244,185,66,0.12));
            border-radius: 12px;
        }
        .result-hero {
            background: linear-gradient(135deg, rgba(47,125,79,0.15), rgba(244,185,66,0.24), rgba(75,163,242,0.14));
            padding: 1.2rem 1.25rem;
            margin-bottom: 1rem;
        }
        .insight-card {
            background: linear-gradient(135deg, rgba(75,163,242,0.14), rgba(244,185,66,0.22), rgba(47,125,79,0.14));
            padding: 1rem 1.1rem;
            margin: 0.85rem 0 1rem 0;
        }
        .stButton > button {
            background: linear-gradient(135deg, #ef6a3c, #d94f70, #f4b942);
            color: white;
            border: none;
            border-radius: 14px;
            font-weight: 800;
        }
        div[data-testid="stProgressBar"] > div > div > div {
            background: linear-gradient(90deg, #2f7d4f, #4ba3f2, #f4b942);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="पशुपहचान", layout="wide")
inject_styles()

language_name = st.selectbox("Language", options=list(LANGUAGE_OPTIONS.keys()), index=0)
t = TEXT[LANGUAGE_OPTIONS[language_name]]

rebuilt_index, indexed_breeds = ensure_reference_index()

if "recognizer" not in st.session_state:
    st.session_state.recognizer = BreedRecognizer(index_path=str(INDEX_PATH))
elif rebuilt_index:
    st.session_state.recognizer = BreedRecognizer(index_path=str(INDEX_PATH))

recognizer: BreedRecognizer = st.session_state.recognizer
backend_label = t["backend_cnn"] if recognizer.backend == "offline-cnn" else t["backend_hand"]
index_status = t["rebuilt"] if rebuilt_index else t["ready"] if indexed_breeds > 0 else t["waiting"]

hero_col, art_col = st.columns([1.2, 0.95], gap="large")
with hero_col:
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-kicker">{t["hero_kicker"]}</div>
            <div class="hero-title">{t["hero_title"]}</div>
            <div class="hero-copy">{t["hero_copy"]}</div>
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
            <div class="metric-label">{t["indexed_breeds"]}</div>
            <div class="metric-value">{indexed_breeds}</div>
            <div class="metric-sub">{t["indexed_breeds_sub"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{t["recognition_mode"]}</div>
            <div class="metric-value" style="font-size:1.25rem;">{backend_label}</div>
            <div class="metric-sub">{t["recognition_mode_sub"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{t["index_status"]}</div>
            <div class="metric-value" style="font-size:1.25rem;">{index_status}</div>
            <div class="metric-sub">{t["index_status_sub"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if recognizer.backend == "offline-cnn":
    st.success(t["offline_cnn"])
else:
    st.warning(t["offline_hand"])

main_col, side_col = st.columns([1.45, 0.9], gap="large")

with side_col:
    st.markdown('<div class="panel-shell">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{t["supported"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-copy">{t["supported_copy"]}</div>', unsafe_allow_html=True)
    st.markdown("".join(f'<span class="breed-chip">{breed}</span>' for breed in INDIAN_CATTLE_BREEDS), unsafe_allow_html=True)
    st.markdown("".join(f'<span class="breed-chip">{breed}</span>' for breed in INDIAN_BUFFALO_BREEDS), unsafe_allow_html=True)
    st.markdown(f'<div class="workflow-note">{t["workflow_note"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with main_col:
    st.markdown('<div class="panel-shell">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{t["upload_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-copy">{t["upload_copy"]}</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(t["upload_label"], type=["jpg", "jpeg", "png", "webp"])
    top_k = st.slider(t["prediction_count"], min_value=1, max_value=5, value=3)

    if uploaded is not None:
        image = Image.open(uploaded)
        st.image(image, caption=t["upload_caption"], use_container_width=True)

        if st.button(t["predict"], type="primary"):
            with st.spinner(t["spinner"]):
                predictions = recognizer.predict(image, top_k=top_k)

            if not predictions:
                st.error(t["no_index"])
            else:
                best = predictions[0]
                insight = BREED_INSIGHTS.get(best.breed)
                st.markdown(
                    f"""
                    <div class="result-hero">
                        <div class="result-label">{t["most_likely"]}</div>
                        <div class="result-breed">{best.breed}</div>
                        <div class="result-copy">
                            {t["confidence"]}: {best.confidence * 100:.1f}%<br>
                            {BREED_DETAILS.get(best.breed, t["breed_fallback"])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if insight:
                    st.markdown(
                        f"""
                        <div class="insight-card">
                            <div class="insight-title">{t["insight_title"]}</div>
                            <div class="insight-trait">{insight["trait"]}</div>
                            <div class="insight-value">{insight["value"]}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                for idx, pred in enumerate(predictions, start=1):
                    st.markdown(f"**{idx}. {pred.breed}**")
                    st.progress(float(pred.confidence), text=f"{pred.confidence * 100:.1f}% {t['match_confidence']}")
                    detail = BREED_DETAILS.get(pred.breed)
                    if detail:
                        st.caption(detail)
    else:
        st.info(t["upload_prompt"])

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="panel-shell" style="margin-top: 1.3rem;">
        <div class="section-title">{t["field_guidance"]}</div>
        <div class="section-copy">{t["field_guidance_copy"]}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
