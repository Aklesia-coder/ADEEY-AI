import os
import pandas as pd
import gradio as gr

# ============================================================
# ADEEY AI — DEPLOYMENT VERSION
# Educational Indigenous Knowledge Explorer
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "elder.png")

# -----------------------------
# Load project data
# -----------------------------

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing required file: {path}. "
            "Make sure the CSV is inside the data/ folder."
        )
    return pd.read_csv(path)


disease_df = load_csv("DISEASE.csv")
symptom_df = load_csv("SYMPTOM.csv")
plant_df = load_csv("PLANT.csv")
mapping_df = load_csv("DISEASE_PLANT_MAPPING.csv")

symptom_df["symptom_name"] = (
    symptom_df["symptom_name"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# -----------------------------
# Disease / plant information
# -----------------------------

def get_disease_information(disease_id):
    disease = disease_df[disease_df["Disease_ID"] == disease_id]

    if disease.empty:
        return None

    row = disease.iloc[0]

    def value(column):
        return str(row[column]) if column in disease.columns else "Not available."

    return {
        "Disease_Name": value("Disease_name"),
        "Category": value("Category"),
        "Description": value("Description"),
        "Cause": value("Cause"),
        "Risk_Factors": value("Risk_factors"),
        "Severity": value("Severity"),
    }


def get_plants_for_disease(disease_id):
    if "Disease_ID" not in mapping_df.columns or "Plant_ID" not in mapping_df.columns:
        return plant_df.iloc[0:0]

    plant_ids = mapping_df[
        mapping_df["Disease_ID"] == disease_id
    ]["Plant_ID"].tolist()

    return plant_df[plant_df["Plant_ID"].isin(plant_ids)]

# -----------------------------
# Symptom normalization / matching
# -----------------------------

SYMPTOM_ALIASES = {
    "fever": "fever",
    "chills": "chills",
    "headache": "headache",
    "sweating": "sweating",
    "cough": "cough",
    "persistent cough": "persistent cough (lasting 2 weeks or more)",
    "persistent cough lasting 2 weeks or more": "persistent cough (lasting 2 weeks or more)",
    "night sweats": "night sweats",
    "weight loss": "weight loss",
    "chest pain": "chest pain",
    "difficulty breathing": "difficulty breathing",
    "shortness of breath": "shortness of breath",
    "severe breathing difficulty": "severe breathing difficulty",
    "diarrhea": "diarrhea",
    "frequent loose or watery stools": "frequent loose or watery stools",
    "abdominal pain": "abdominal pain",
    "vomiting": "vomiting",
    "bloating": "bloating",
    "abdominal bloating": "abdominal bloating",
    "urgent need to have a bowel movement": "urgent need to have a bowel movement",
    "little or no urination": "little or no urination",
    "confusion or lethargy": "confusion or lethargy",
    "blood in stool": "blood in stool",
    "itching around anus": "itching around the anus",
    "itching around the anus": "itching around the anus",
}


def normalize_user_symptoms(user_symptoms):
    normalized = []

    for symptom in user_symptoms:
        symptom = str(symptom).strip().lower()

        if not symptom:
            continue

        symptom = SYMPTOM_ALIASES.get(symptom, symptom)
        normalized.append(symptom)

    return list(dict.fromkeys(normalized))


def symptom_matches(user_symptom, database_symptom):
    user_symptom = str(user_symptom).strip().lower()
    database_symptom = str(database_symptom).strip().lower()

    if user_symptom == database_symptom:
        return True

    equivalents = {
        "chest pain": [
            "chest pain",
            "chest pain (especially when breathing or coughing)",
        ],
        "persistent cough (lasting 2 weeks or more)": [
            "persistent cough",
            "persistent cough (lasting 2 weeks or more)",
        ],
        "itching around the anus": [
            "itching around anus",
            "itching around the anus",
        ],
        "diarrhea": ["diarrhea"],
        "difficulty breathing": ["difficulty breathing"],
    }

    for key, values in equivalents.items():
        if user_symptom == key and database_symptom in values:
            return True

    return False

# -----------------------------
# Final prediction engine
# -----------------------------

def final_prediction(user_symptoms):
    normalized = normalize_user_symptoms(user_symptoms)
    results = {}

    for disease_id in symptom_df["Disease_ID"].unique():
        rows = symptom_df[symptom_df["Disease_ID"] == disease_id]

        database_symptoms = [
            str(x).strip().lower()
            for x in rows["symptom_name"]
        ]

        matched = []

        for user_symptom in normalized:
            if any(
                symptom_matches(user_symptom, database_symptom)
                for database_symptom in database_symptoms
            ):
                matched.append(user_symptom)

        matched = list(dict.fromkeys(matched))
        coverage = (len(matched) / len(normalized) * 100) if normalized else 0

        results[disease_id] = {
            "Matched_Symptoms": matched,
            "Coverage": round(coverage, 2),
            "Match_Count": len(matched),
        }

    return results


def get_best_result(results):
    if not results:
        return None, "unknown"

    ranked = sorted(
        results.items(),
        key=lambda x: (x[1]["Match_Count"], x[1]["Coverage"]),
        reverse=True,
    )

    highest_count = ranked[0][1]["Match_Count"]

    if highest_count == 0:
        return None, "unknown"

    tied = [
        disease_id
        for disease_id, data in ranked
        if data["Match_Count"] == highest_count
    ]

    if len(tied) > 1:
        return tied, "ambiguous"

    return tied[0], "match"

# -----------------------------
# References
# -----------------------------

ADEEY_REFERENCES = [
    {
        "name": "WHO — Global Traditional Medicine Strategy 2025–2034",
        "url": "https://www.who.int/publications/i/item/9789240113176",
    },
    {
        "name": "WHO — Traditional, Complementary and Integrative Medicine",
        "url": "https://www.who.int/health-topics/traditional-complementary-and-integrative-medicine",
    },
    {
        "name": "WHO — Malaria",
        "url": "https://www.who.int/health-topics/malaria",
    },
    {
        "name": "WHO — Tuberculosis",
        "url": "https://www.who.int/health-topics/tuberculosis",
    },
    {
        "name": "WHO — Diarrhoeal Disease",
        "url": "https://www.who.int/en/news-room/fact-sheets/detail/diarrhoeal-disease",
    },
    {
        "name": "PubMed — Endemic medicinal plants of Ethiopia",
        "url": "https://pubmed.ncbi.nlm.nih.gov/35452775/",
    },
]


def get_reference_markdown():
    text = "## 📚 References\n\n"
    for ref in ADEEY_REFERENCES:
        text += f"- [{ref['name']}]({ref['url']})\n"
    return text

# -----------------------------
# Response generator
# -----------------------------

def generate_final_response(user_symptoms):
    if not user_symptoms:
        return "# 🩺 ADEEY AI\n\n⚠️ Please enter at least one symptom."

    results = final_prediction(user_symptoms)
    best, status = get_best_result(results)

    response = (
        "# 🩺 ADEEY AI\n\n"
        "This information is for **educational purposes only.**\n\n"
        "---\n\n"
    )

    if status == "unknown":
        response += (
            "## ⚠️ Not enough matching information\n\n"
            "I could not find a strong enough match in my current educational database.\n\n"
            "Please provide additional or more specific symptoms to explore the indigenous knowledge.\n\n"
            "A weak symptom match should not be interpreted as a diagnosis.\n\n"
            "---\n\n"
            + get_reference_markdown()
        )
        return response

    if status == "ambiguous":
        response += (
            "## ⚠️ Overlapping symptom information\n\n"
            "The symptoms you entered match more than one condition in the educational database.\n\n"
            "### Possible database matches\n\n"
        )

        for disease_id in best:
            info = get_disease_information(disease_id)
            data = results[disease_id]
            if info:
                response += f"### {info['Disease_Name']}\n\n"
                response += "**Matched symptoms:** " + ", ".join(data["Matched_Symptoms"]) + "\n\n"

        response += (
            "Please provide more specific symptoms to explore the educational information more precisely.\n\n"
            "---\n\n"
            + get_reference_markdown()
            + "\n---\n\n"
            "⚠️ **Educational use only. This is not a diagnosis.**"
        )
        return response

    info = get_disease_information(best)
    data = results[best]

    if info is None:
        return response + "⚠️ Disease information is unavailable for this database record."

    response += f"## Possible Condition\n\n### {info['Disease_Name']}\n\n"
    response += "### 📊 Symptom Coverage\n\n"
    response += f"**{data['Coverage']}%**\n\n"
    response += (
        "This percentage represents how many of your entered symptoms matched this database record. "
        "It is **not a medical probability or diagnosis**.\n\n"
    )

    response += "### 🔎 Matched Symptoms\n\n"
    for symptom in data["Matched_Symptoms"]:
        response += f"- {symptom}\n"

    response += f"\n### 📖 Description\n\n{info['Description']}\n\n"
    response += f"### 🦠 Cause\n\n{info['Cause']}\n\n"
    response += f"### ⚠️ Risk Factors\n\n{info['Risk_Factors']}\n\n"
    response += f"### 🚨 Severity\n\n{info['Severity']}\n\n"

    plants = get_plants_for_disease(best)
    response += "---\n\n## 🌿 Ethiopian Medicinal Plants\n\n"

    if len(plants) > 0:
        for _, plant in plants.iterrows():
            response += f"### 🌱 {plant.get('Plant_Name', 'Unknown plant')}\n\n"
            response += f"**Scientific Name:** {plant.get('scientific_name', 'Not available.')}\n\n"
            response += f"**Local Name:** {plant.get('Local_name', 'Not available.')}\n\n"
            response += f"**Traditional Use:** {plant.get('traditional_use', 'Not available.')}\n\n"
            response += f"**Safety Warning:** {plant.get('safety_warning', 'Not available.')}\n\n"
    else:
        response += "No plant information is available for this database record.\n\n"

    response += "---\n\n" + get_reference_markdown()
    response += (
        "\n---\n\n"
        "### ⚠️ Educational Safety Notice\n\n"
        "Adeey AI provides educational information only. "
        "It does not diagnose diseases or replace professional medical care."
    )

    return response


def ask_addey(symptom_text):
    if symptom_text is None or not str(symptom_text).strip():
        return (
            "## 🩺 ADEEY AI\n\n"
            "⚠️ Enter a symptom to explore indigenous knowledge."
        )

    symptoms = [
        symptom.strip().lower()
        for symptom in str(symptom_text).split(",")
        if symptom.strip()
    ]

    return generate_final_response(symptoms)

# -----------------------------
# Interface
# -----------------------------

css = """
:root {
    --bg: #0d1117;
    --surface: #161b22;
    --surface-2: #1c2128;
    --border: #2d333b;
    --accent: #2ea043;
    --accent-hover: #3fb950;
    --text: #e6edf3;
    --text-dim: #8b949e;
}

body, .gradio-container {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.gradio-container {
    max-width: 900px !important;
    margin: auto !important;
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}

#logo img {
    width: 120px !important;
    height: 120px !important;
    object-fit: cover !important;
    border-radius: 50% !important;
    border: 3px solid var(--accent) !important;
    margin: 10px auto !important;
    display: block !important;
    box-shadow: 0 0 25px rgba(46, 160, 67, 0.35);
}

.title { text-align: center; }
.title h1 {
    font-size: 34px;
    margin-bottom: 2px;
    color: var(--text);
}
.title h3 {
    color: var(--accent);
    font-weight: 500;
    margin-top: 0;
}
.title p { color: var(--text-dim); font-size: 15px; }

.card {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 18px !important;
    margin-bottom: 14px !important;
}

button {
    border-radius: 10px !important;
    font-weight: 600 !important;
}

.primary-btn button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
}

.primary-btn button:hover { background: var(--accent-hover) !important; }

.ghost-btn button {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

.ghost-btn button:hover { border-color: var(--accent) !important; }

textarea, input {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

#response {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 16px !important;
}

@media (max-width: 600px) {
    .title h1 { font-size: 26px; }
    #logo img { width: 90px !important; height: 90px !important; }
}
"""


def show_main():
    return gr.Column(visible=False), gr.Column(visible=True)


def show_welcome():
    return gr.Column(visible=True), gr.Column(visible=False)


with gr.Blocks(title="ADEEY AI") as demo:
    with gr.Column(visible=True) as welcome_page:
        if os.path.exists(LOGO_PATH):
            gr.Image(value=LOGO_PATH, show_label=False, container=False, elem_id="logo")

        gr.Markdown(
            """
<div class="title">

# 🩺 ADEEY AI
### Ethiopian Indigenous Medicine Assistant

<p>Explore educational information about symptoms, diseases,<br>
and traditional Ethiopian medicinal plants.</p>
</div>
"""
        )

        with gr.Column(elem_classes="card"):
            gr.Markdown(
                """
**⚠️ Important**

Adeey AI is an educational information system.
It does not provide medical diagnosis or replace professional medical care.
"""
            )

        start_button = gr.Button("🚀 Start ADEEY AI", elem_classes="primary-btn")

        with gr.Column(elem_classes="card"):
            gr.Markdown(
                """
### What you can explore
- 🔎 Symptom-based educational information
- 🌿 Ethiopian medicinal plants
- 📖 Disease information
- 📚 References and sources
"""
            )

    with gr.Column(visible=False) as main_page:
        with gr.Row():
            with gr.Column(scale=1, min_width=100):
                if os.path.exists(LOGO_PATH):
                    gr.Image(value=LOGO_PATH, show_label=False, container=False, elem_id="logo")
            with gr.Column(scale=4):
                gr.Markdown(
                    """
<div class="title" style="text-align:left;">

# 🩺 ADEEY AI
### Ethiopian Indigenous Medicine Assistant
</div>
"""
                )

        with gr.Column(elem_classes="card"):
            gr.Markdown(
                """
Enter symptoms separated by commas.

**Example:** `fever, chills, headache`
or `cough, chest pain, difficulty breathing`
"""
            )

            symptoms_box = gr.Textbox(
                label="Symptoms",
                placeholder="Example: fever, chills, headache",
                lines=3,
            )

            with gr.Row():
                example_malaria = gr.Button("🌡 Malaria", elem_classes="ghost-btn")
                example_tb = gr.Button("🫁 TB", elem_classes="ghost-btn")
                example_pneumonia = gr.Button("🫁 Pneumonia", elem_classes="ghost-btn")

            with gr.Row():
                ask_button = gr.Button("🔎 Explore Symptoms", elem_classes="primary-btn")
                clear_button = gr.ClearButton(elem_classes="ghost-btn")

        output_box = gr.Markdown(
            value="### 🩺 ADEEY AI\n\nEnter your symptoms above.",
            elem_id="response",
        )

        clear_button.add([symptoms_box, output_box])
        back_button = gr.Button("← Back to Welcome", elem_classes="ghost-btn")

    start_button.click(
        show_main,
        outputs=[welcome_page, main_page],
    )

    back_button.click(
        show_welcome,
        outputs=[welcome_page, main_page],
    )

    ask_button.click(
        ask_addey,
        inputs=symptoms_box,
        outputs=output_box,
    )

    example_malaria.click(
        lambda: "fever, chills, headache",
        outputs=symptoms_box,
    )
    example_tb.click(
        lambda: "persistent cough, night sweats, weight loss",
        outputs=symptoms_box,
    )
    example_pneumonia.click(
        lambda: "cough, chest pain, difficulty breathing",
        outputs=symptoms_box,
    )


if __name__ == "__main__":
    demo.launch(css=css)
