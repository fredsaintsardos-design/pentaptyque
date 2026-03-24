import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import hmac
import io
import os
import tempfile
import csv
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PENTAPTYQUE — REMATCH",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── AUTHENTIFICATION ─────────────────────────────
def check_coach_password():
    def password_entered():
        if hmac.compare_digest(
            st.session_state["coach_password"],
            st.secrets["coach_password"]
        ):
            st.session_state["coach_authenticated"] = True
            del st.session_state["coach_password"]
        else:
            st.session_state["coach_authenticated"] = False

    if st.session_state.get("coach_authenticated", False):
        return True

    st.markdown("### Accès coach")
    st.text_input(
        "Mot de passe coach",
        type="password",
        on_change=password_entered,
        key="coach_password"
    )

    if "coach_authenticated" in st.session_state and not st.session_state["coach_authenticated"]:
        st.error("Mot de passe coach incorrect")

    return False


# ─── SAUVEGARDE DES RÉPONSES ──────────────────────
def save_answers_to_csv(prenom, nom, answers, engagement=""):
    filename = "reponses_pentaptyque.csv"

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prenom": prenom,
        "nom": nom,
        "engagement": engagement,
    }

    row.update(answers)

    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    # Page de login
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@900&family=Barlow:wght@300;400;700&display=swap');
    html, body, [class*="css"] { 
    font-family: 'Barlow', sans-serif !important; 
    background: #f7f9fb !important; 
}
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { max-width: 420px !important; padding-top: 10vh !important; }
    div.stButton > button {
        background: #0cc0df !important; color: #0a0a0a !important;
        font-weight: 900 !important; letter-spacing: 3px !important;
        text-transform: uppercase !important; font-size: 11px !important;
        padding: 14px 40px !important; border: none !important;
        border-radius: 0 !important; width: 100% !important;
    }
    div[data-testid="stTextInput"] input {
    background: rgba(12,192,223,0.10) !important;
    border: 2px solid #0cc0df !important;
    border-radius: 6px !important;
    color: #0f172a !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 14px !important;
    padding: 12px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #0cc0df !important;
    box-shadow: 0 0 0 2px rgba(12,192,223,0.2) !important;
}
    div[data-testid="stTextInput"] input:focus { border-color: #0cc0df !important; box-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
<div style="text-align:center; margin-bottom: 40px;">
    <div style="font-family:'Barlow Condensed', sans-serif; font-size:46px; font-weight:900; color:#0f172a; line-height:1;">
        PENTAPTYQUE
    </div>
    <div style="font-size:9px; letter-spacing:4px; color:#555; text-transform:uppercase; margin-top:6px;">
        REMATCH - Accès privé
    </div>
</div>
""", unsafe_allow_html=True)

    st.text_input(
        "Mot de passe",
        type="password",
        placeholder="Entrez votre mot de passe",
        on_change=password_entered,
        key="password",
        label_visibility="collapsed"
    )

    if "authenticated" in st.session_state and not st.session_state["authenticated"]:
        st.markdown('<div style="color:#e05a5a; font-size:12px; text-align:center; margin-top:8px; letter-spacing:1px;">Mot de passe incorrect</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px; color:#333; text-align:center; margin-top:32px; letter-spacing:2px;">© REMATCH — Document confidentiel</div>', unsafe_allow_html=True)
    return False

if mode == "Participant":
    if not check_password():
        st.stop()

if mode == "Coach":
    if not check_coach_password():
        st.stop()
    
    mode = st.radio(
    "Accès",
    ["Participant", "Coach"],
    horizontal=True,
    label_visibility="collapsed"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700;900&family=Barlow+Condensed:wght@700;900&display=swap');

:root {
    --primary: #0cc0df;
    --primary-dark: #0b2a3a;
    --primary-light: rgba(12,192,223,0.10);

    --background: #f7f9fb;
    --white: #ffffff;
    --text: #1f2933;

    --grey-light: #e5e7eb;
    --grey-mid: #9ca3af;
    --grey-dark: #4b5563;

    --danger: #ef4444;
    --warn: #f59e0b;
}

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif !important;
    background-color: var(--background) !important;
    color: var(--text) !important;
}

/* Hide Streamlit default elements */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Largeur page */
.block-container {
    padding-top: 0 !important;
    max-width: 900px !important;
}

/* Champ mot de passe */
div[data-testid="stTextInput"] input {
    background: var(--primary-light) !important;
    border: 2px solid var(--primary) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    padding: 12px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: var(--primary-dark) !important;
    box-shadow: 0 0 0 2px var(--primary-light) !important;
}

/* Top header */
.rematch-header {
    background: white;
    padding: 18px 36px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--grey-light);
    margin: -1rem -1rem 0 -1rem;
}

.rematch-header .brand {
    color: var(--primary-dark);
    font-weight: 900;
    font-size: 22px;
    letter-spacing: 4px;
    font-family: 'Barlow Condensed', sans-serif;
}

.rematch-header .tag {
    color: var(--grey-dark);
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* Hero */
.hero {
    background: linear-gradient(90deg, #eef3f7 0%, #f7f9fb 100%);
    color: var(--text);
    padding: 60px 36px 50px;
    margin: 0 -1rem 2rem -1rem;
    border-bottom: 2px solid var(--primary);
}

.hero h1 {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 68px;
    font-weight: 900;
    letter-spacing: 1px;
    color: var(--primary-dark);
    margin: 0 0 10px 0;
    line-height: 1;
}

.hero h1 span {
    color: var(--primary);
}

.hero .subtitle {
    font-size: 11px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--grey-dark);
    margin-bottom: 20px;
}

.hero p {
    font-size: 16px;
    color: var(--text);
    line-height: 1.7;
    max-width: 720px;
    font-weight: 400;
}

/* Dimension header */
.dim-header {
    background: white;
    border-left: 5px solid var(--primary);
    padding: 20px 24px;
    margin: 24px 0 20px 0;
    border-radius: 0;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}

.dim-header .dim-num {
    font-size: 9px;
    letter-spacing: 3px;
    color: var(--primary);
    text-transform: uppercase;
    margin-bottom: 4px;
    font-weight: 700;
}

.dim-header .dim-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 28px;
    font-weight: 900;
    color: var(--primary-dark);
    margin-bottom: 4px;
}

.dim-header .dim-obj {
    font-size: 12px;
    color: var(--grey-dark);
    font-style: italic;
    font-weight: 300;
}

/* Sections */
.sub-section-title {
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--grey-dark);
    font-weight: 700;
    border-bottom: 1px solid var(--grey-light);
    padding-bottom: 8px;
    margin: 28px 0 14px 0;
}

/* Questions */
.q-num {
    font-size: 14px;
    font-weight: 700;
    color: var(--grey-dark);
}

/* Result cards */
.result-card {
    background: white;
    color: var(--text);
    padding: 22px 20px;
    margin-bottom: 10px;
    border-left: 4px solid var(--primary);
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}

.result-card.warn {
    border-left-color: var(--warn);
}

.result-card.danger {
    border-left-color: var(--danger);
}

.result-card .dim-name {
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--grey-dark);
    margin-bottom: 4px;
}

.result-card .score-big {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 36px;
    font-weight: 900;
    color: var(--primary);
}

.result-card.warn .score-big {
    color: var(--warn);
}

.result-card.danger .score-big {
    color: var(--danger);
}

.result-card .interp {
    font-size: 13px;
    color: var(--text);
    font-weight: 400;
    line-height: 1.6;
    margin-top: 6px;
}

/* Cross cards */
.cross-card {
    background: white;
    border-left: 3px solid var(--primary);
    padding: 16px 18px;
    margin-bottom: 10px;
    font-size: 13px;
    line-height: 1.6;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}

.cross-card.warn {
    border-left-color: var(--warn);
    background: #fffbf5;
}

.cross-card.danger {
    border-left-color: var(--danger);
    background: #fff8f8;
}

/* Scale legend */
.scale-legend {
    display: flex;
    gap: 4px;
    margin-bottom: 16px;
}

.scale-item {
    flex: 1;
    background: white;
    color: var(--grey-dark);
    text-align: center;
    padding: 8px 4px;
    font-size: 9px;
    letter-spacing: 1px;
    text-transform: uppercase;
    border: 1px solid var(--grey-light);
}

.scale-item span {
    display: block;
    color: var(--primary-dark);
    font-size: 18px;
    font-weight: 900;
}

/* Radio buttons */
div[data-testid="stRadio"] > label {
    display: none !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] {
    flex-direction: row !important;
    gap: 8px !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label {
    background: white !important;
    border: 2px solid var(--grey-light) !important;
    padding: 6px 14px !important;
    border-radius: 0 !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    min-width: 42px !important;
    text-align: center !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
    color: #0a0a0a !important;
}

/* Buttons */
div.stButton > button {
    background: var(--primary) !important;
    color: #0a0a0a !important;
    font-weight: 900 !important;
    font-family: 'Barlow', sans-serif !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
    padding: 14px 40px !important;
    border: none !important;
    border-radius: 0 !important;
    width: 100% !important;
    transition: background 0.15s !important;
}

div.stButton > button:hover {
    background: var(--primary-dark) !important;
    color: white !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: white !important;
}

/* Divider */
hr {
    border-color: var(--grey-light) !important;
}

/* Alerts */
.stAlert {
    border-radius: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
DIMENSIONS_DATA = {
    "Physique": {
        "icon": "●",
        "objective": "Évaluer votre niveau d'énergie, de vitalité et votre hygiène de récupération.",
        "sections": {
            "Énergie et vitalité": [
                "Mon niveau d'énergie reste stable tout au long de la journée.",
                "Je me sens globalement en forme dans mes activités quotidiennes.",
                "Je dispose de suffisamment d'énergie pour assumer mes responsabilités.",
                "Je ressens rarement des baisses d'énergie prolongées.",
                "Je sais identifier les moments de la journée où je suis le plus performant.",
            ],
            "Sommeil et récupération": [
                "Mon sommeil est régulier et réparateur.",
                "Je dors en moyenne le nombre d'heures dont j'ai besoin.",
                "Je récupère efficacement après des périodes de forte activité.",
                "Je respecte des horaires de sommeil cohérents.",
                "Je ressens rarement une fatigue accumulée.",
            ],
            "Activité physique": [
                "Je pratique une activité physique régulière.",
                "Je prends soin de ma mobilité et de ma posture.",
                "J'intègre des moments de mouvement dans ma journée (marche, étirements...).",
                "Je perçois un lien direct entre mon activité physique et mon efficacité professionnelle.",
                "Je considère la forme physique comme un levier de performance durable.",
            ],
            "Nutrition et hygiène de vie": [
                "Mon alimentation est équilibrée et adaptée à mon rythme de vie.",
                "Je m'hydrate suffisamment au quotidien.",
                "Je limite les excès qui nuisent à mon bien-être.",
                "Je prends le temps de véritables pauses repas.",
                "Mon hygiène de vie soutient mon niveau d'énergie.",
            ],
            "Gestion du stress corporel": [
                "Je sais détecter les signaux physiques de tension ou de surmenage.",
                "J'utilise des moyens efficaces pour relâcher la pression (respiration, marche, relaxation...).",
                "Mon corps récupère bien après des périodes stressantes.",
                "Je ressens une bonne coordination entre mon corps et mon esprit.",
                "Mon rythme de vie actuel est globalement soutenable sur la durée.",
            ],
        }
    },
    "Mental": {
        "icon": "◆",
        "objective": "Explorer la clarté de pensée, la concentration et la discipline mentale.",
        "sections": {
            "Clarté et concentration": [
                "Je parviens à rester concentré sur une tâche sans me disperser.",
                "J'ai une vision claire de mes priorités du moment.",
                "Je sais faire abstraction des distractions lorsque c'est nécessaire.",
                "Je prends le temps d'analyser les situations avant d'agir.",
                "J'entretiens ma capacité de réflexion et d'apprentissage.",
            ],
            "Gestion de la charge mentale": [
                "Je parviens à déconnecter mentalement après le travail.",
                "Je gère efficacement la quantité d'informations que je reçois.",
                "J'évite de ruminer ou de repasser sans cesse les mêmes pensées.",
                "Je me sens globalement serein face à mes obligations.",
                "J'ai trouvé un bon équilibre entre exigence et lâcher-prise.",
            ],
            "Discipline et priorisation": [
                "Je planifie mes tâches de manière organisée.",
                "Je respecte la plupart des engagements que je me fixe.",
                "Je distingue clairement l'urgent de l'important.",
                "J'avance régulièrement vers mes objectifs sans procrastiner.",
                "Je sais dire non quand c'est nécessaire.",
            ],
            "Adaptabilité cognitive": [
                "J'accueille les changements avec une attitude ouverte.",
                "Je sais revoir mes positions quand les faits m'y invitent.",
                "J'aime sortir de ma zone de confort intellectuelle.",
                "Je m'adapte rapidement à de nouveaux contextes ou interlocuteurs.",
                "Je cherche activement à améliorer mes méthodes de travail.",
            ],
            "Résilience et mental de croissance": [
                "Je rebondis rapidement après un échec ou un contretemps.",
                "Je vois les difficultés comme des occasions d'apprendre.",
                "Je garde confiance même dans les périodes de forte incertitude.",
                "Je persévère jusqu'à atteindre mes objectifs.",
                "Je me considère comme capable de progresser en continu.",
            ],
        }
    },
    "Émotionnel": {
        "icon": "▲",
        "objective": "Évaluer votre conscience émotionnelle, votre stabilité et votre relation aux autres.",
        "sections": {
            "Conscience de soi": [
                "Je suis capable d'identifier mes émotions dans les moments clés.",
                "Je perçois l'impact de mes émotions sur mes décisions.",
                "Je sais reconnaître les situations qui me mettent sous tension.",
                "J'observe mes réactions émotionnelles avec lucidité.",
                "J'arrive à exprimer ce que je ressens sans difficulté.",
            ],
            "Régulation émotionnelle": [
                "Je reste calme dans les situations tendues.",
                "Je parviens à retrouver rapidement mon équilibre émotionnel après un conflit.",
                "Je gère efficacement le stress émotionnel.",
                "Je ne me laisse pas envahir par la colère ou la frustration.",
                "J'utilise des stratégies concrètes pour apaiser mes émotions (respiration, recul, dialogue...).",
            ],
            "Relations interpersonnelles": [
                "J'entretiens des relations de confiance avec mes collègues ou partenaires.",
                "Je sais instaurer un climat de respect mutuel.",
                "J'aborde les désaccords avec ouverture et respect.",
                "Je favorise un environnement de travail positif.",
                "Je me sens entouré et soutenu dans mon environnement professionnel.",
            ],
            "Empathie et écoute": [
                "Je fais preuve d'écoute réelle dans mes échanges.",
                "Je cherche à comprendre les besoins et points de vue des autres.",
                "Je prends en compte les émotions de mes interlocuteurs.",
                "Je m'adapte à la sensibilité émotionnelle de chacun.",
                "Je favorise des interactions constructives et bienveillantes.",
            ],
            "Confiance et équilibre intérieur": [
                "Je me sens globalement à ma place dans mon rôle actuel.",
                "J'ai confiance dans ma capacité à gérer les situations complexes.",
                "Je ressens un bon équilibre entre exigence et bienveillance envers moi-même.",
                "Je garde une attitude positive même en période de tension.",
                "Je me sens aligné intérieurement.",
            ],
        }
    },
    "Sens": {
        "icon": "★",
        "objective": "Explorer le cap, la motivation et la cohérence personnelle.",
        "sections": {
            "Alignement valeurs / actions": [
                "Mes décisions reflètent mes valeurs profondes.",
                "Je me sens cohérent entre ce que je dis et ce que je fais.",
                "Je refuse les actions qui vont à l'encontre de mes convictions.",
                "Mes choix professionnels sont en accord avec ce que je juge important.",
                "Je ressens de la fierté dans ce que j'entreprends.",
            ],
            "Vision et cap personnel": [
                "J'ai une vision claire de ma trajectoire professionnelle.",
                "Je sais où je veux être dans trois ans.",
                "Mes objectifs sont cohérents avec ma vision à long terme.",
                "Je me fixe des caps stimulants et atteignables.",
                "J'entretiens une vision globale, au-delà du court terme.",
            ],
            "Motivation intrinsèque": [
                "Je suis motivé avant tout par le sens de mes actions, plus que par la reconnaissance.",
                "Je ressens de l'enthousiasme dans mes projets actuels.",
                "Je me lève le matin avec envie et curiosité.",
                "Mon travail m'apporte un sentiment d'utilité.",
                "Je sais raviver ma motivation quand elle baisse.",
            ],
            "Contribution et impact": [
                "J'ai le sentiment de contribuer à quelque chose qui compte.",
                "Mon rôle a un impact positif sur mon environnement.",
                "Je me sens utile dans mon organisation ou ma communauté.",
                "Je perçois clairement la valeur que j'apporte.",
                "Je cherche à laisser une trace constructive.",
            ],
            "Cohérence et satisfaction globale": [
                "Je ressens une cohérence entre mes différentes sphères de vie.",
                "J'ai un bon équilibre entre ambitions et bien-être personnel.",
                "Je suis globalement satisfait de la direction que prend ma vie.",
                "Je vis selon mes propres priorités, pas uniquement celles des autres.",
                "Je perçois du sens dans la plupart de mes activités.",
            ],
        }
    },
    "Comportemental": {
        "icon": "⬡",
        "objective": "Observer les modes d'action, la mise en mouvement et le leadership au quotidien.",
        "sections": {
            "Passage à l'action": [
                "Je passe à l'action rapidement une fois mes décisions prises.",
                "Je transforme mes intentions en actes concrets.",
                "Je respecte mes engagements et mes délais.",
                "Je maintiens mes efforts même quand les résultats tardent.",
                "Je fais preuve d'initiative sans attendre qu'on me sollicite.",
            ],
            "Communication et influence": [
                "J'exprime mes idées avec clarté et conviction.",
                "Je sais écouter activement mes interlocuteurs.",
                "J'adapte mon message selon mon audience.",
                "Je favorise un dialogue ouvert et constructif.",
                "Je sais mobiliser les autres autour d'un objectif commun.",
            ],
            "Gestion du temps": [
                "Je planifie mes priorités chaque semaine.",
                "Je gère efficacement mon agenda.",
                "J'accorde du temps aux sujets vraiment stratégiques.",
                "Je prévois des temps de récupération dans mon emploi du temps.",
                "Je respecte un bon équilibre entre disponibilité et protection de mon temps.",
            ],
            "Leadership et exemplarité": [
                "Je donne l'exemple par mes comportements.",
                "Je soutiens mes équipes dans les moments clés.",
                "Je fixe un cadre clair et des attentes explicites.",
                "J'encourage la prise d'initiative autour de moi.",
                "Je cherche à inspirer confiance par mes actes.",
            ],
            "Capacité d'apprentissage et d'adaptation": [
                "Je tire des enseignements de mes expériences.",
                "Je cherche activement à progresser dans mon rôle.",
                "J'accepte la remise en question comme un levier de croissance.",
                "Je reste curieux et ouvert à de nouvelles pratiques.",
                "J'intègre rapidement les retours que je reçois.",
            ],
        }
    },
}

DIM_COLORS = {
    "Physique": "#0cc0df",
    "Mental": "#38bdf8",
    "Émotionnel": "#818cf8",
    "Sens": "#34d399",
    "Comportemental": "#fb923c",
}

COMMENTS = {
    "Physique": {
        "high":  "Vous disposez d'un bon niveau d'énergie et d'une hygiène de vie solide.",
        "mid":   "L'énergie est globalement stable mais perfectible ; attention à la récupération.",
        "low":   "Fatigue ou déséquilibre énergétique : à traiter en priorité par un recentrage sur le sommeil et les rituels physiques.",
    },
    "Mental": {
        "high":  "Vous démontrez une forte clarté mentale et une bonne capacité de focus.",
        "mid":   "Vous gérez bien la charge mentale mais pourriez fluidifier votre organisation.",
        "low":   "Charge cognitive excessive, dispersion : besoin de simplification et d'ancrage.",
    },
    "Émotionnel": {
        "high":  "Bonne conscience de soi et maîtrise émotionnelle.",
        "mid":   "Équilibre global, vigilance sur la gestion des tensions.",
        "low":   "Émotions refoulées ou mal canalisées : nécessité de renforcer la régulation et l'expression.",
    },
    "Sens": {
        "high":  "Vision claire et cohérente, forte motivation intrinsèque.",
        "mid":   "Bon alignement mais parfois un manque de clarté sur le moyen terme.",
        "low":   "Perte de sens, démotivation ou incohérence valeurs/actions : à clarifier en accompagnement.",
    },
    "Comportemental": {
        "high":  "Passage à l'action fluide et leadership inspirant.",
        "mid":   "Action stable mais perfectible (planification, priorisation).",
        "low":   "Difficulté à concrétiser ou manque de cap : focus sur la structuration comportementale.",
    },
}

def get_level(score):
    if score >= 80: return "high", "🟢 Zone d'appui", "#0cc0df"
    if score >= 60: return "mid", "🟠 Zone à renforcer", "#f0a050"
    return "low", "🔴 Zone de vigilance", "#e05a5a"

def score_sur_100(brut):
    return round((brut / 125) * 100)

def build_radar_image(scores_100):
    labels = list(scores_100.keys())
    values = list(scores_100.values())

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8)
    ax.set_ylim(0, 100)

    img_buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    img_buffer.seek(0)

    return img_buffer

def build_pdf(prenom, nom, scores_100, dimension_forte, dimension_fragile, moyenne_globale, engagement):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    left = 50
    top = height - 50
    y = top

    # Logo
    try:
        pdf.drawImage("logo_rematch.png", 50, height - 90, width=120, preserveAspectRatio=True, mask='auto')
    except:
        pass

    y = top - 40

    # Titre
    from reportlab.lib import colors
    pdf.setTitle("Bilan Pentaptyque REMATCH")
    pdf.setFillColor(colors.HexColor("#0cc0df"))
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(left, y, "BILAN PENTAPTYQUE — REMATCH")
    pdf.setFillColor(colors.black)
    y -= 24

    pdf.setFont("Helvetica", 10)
    pdf.drawString(left, y, "Document confidentiel")
    y -= 28

    # Identité
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Participant")
    y -= 16

    pdf.setFont("Helvetica", 11)
    pdf.drawString(left, y, f"Nom : {prenom} {nom}".strip())
    y -= 16
    pdf.drawString(left, y, f"Score global : {moyenne_globale}/100")
    y -= 16
    pdf.drawString(left, y, f"Dimension d'appui dominante : {dimension_forte} ({scores_100[dimension_forte]}/100)")
    y -= 16
    pdf.drawString(left, y, f"Dimension prioritaire à renforcer : {dimension_fragile} ({scores_100[dimension_fragile]}/100)")
    y -= 28

    # Scores
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Scores par dimension")
    y -= 18

    pdf.setFont("Helvetica", 11)
    for dim, score in scores_100.items():
        pdf.drawString(left, y, f"- {dim} : {score}/100")
        y -= 15

    y -= 10

    # Radar chart via matplotlib
    try:
        radar_buffer = build_radar_image(scores_100)
        image = ImageReader(radar_buffer)

        img_width = 420
        img_height = 320

        if y - img_height < 80:
            pdf.showPage()
            y = top

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(left, y, "Profil visuel")
        y -= 18
        pdf.drawImage(
            image,
            left,
            y - img_height,
            width=img_width,
            height=img_height,
            preserveAspectRatio=True,
            mask='auto'
        )
        y -= img_height + 20

    except Exception as e:
        pdf.setFont("Helvetica", 10)
        pdf.drawString(left, y, f"Radar non intégré : {str(e)[:120]}")
        y -= 20

    # Engagement
    if y < 140:
        pdf.showPage()
        y = top

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Premier engagement")
    y -= 18

    pdf.setFont("Helvetica", 11)
    engagement_text = engagement.strip() if engagement else "Non renseigné"

    max_chars = 95
    words = engagement_text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(test_line) <= max_chars:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    for line in lines:
        pdf.drawString(left, y, line)
        y -= 15
        if y < 60:
            pdf.showPage()
            y = top

    pdf.setFont("Helvetica", 9)
    pdf.drawString(left, 30, "© REMATCH — Bilan Pentaptyque")

    pdf.save()
    buffer.seek(0)
    return buffer

# ─── INIT SESSION STATE ───────────────────────────────────────────────────────
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "prenom" not in st.session_state:
    st.session_state.prenom = ""
if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = None

# ─── HEADER ───────────────────────────────────────────────────────────────────
col_logo, col_tag = st.columns([4, 2])

with col_logo:
    st.markdown('<div style="padding-top:10px;">', unsafe_allow_html=True)
    st.image("logo_rematch.png", width=260)
    st.markdown('</div>', unsafe_allow_html=True)

with col_tag:
    st.markdown("""
    <div style="text-align:right; padding-top:24px; font-size:12px; letter-spacing:3px; color:#6b7280;">
        COACHING & PERFORMANCE
    </div>
    """, unsafe_allow_html=True)

# ─── HERO ─────────────────────────────────────────────────────────────────────
if not st.session_state.submitted:
    st.markdown("""
    <div class="hero">
      <div class="subtitle">Audit de performance 5D</div>
      <h1>PENTA<span>PTYQUE</span></h1>
      <p>
        Ce questionnaire n'est pas un test de personnalité mais une photographie globale
        de votre fonctionnement dans cinq dimensions interdépendantes :<br/>
        <strong style="color:white;">Physique — Mental — Émotionnel — Sens — Comportemental.</strong><br/><br/>
        Répondez à chaque affirmation selon votre ressenti actuel, sur une échelle de <strong style="color:#0cc0df;">1 à 5</strong>.
        Les résultats vous permettront, avec votre coach, d'identifier vos points d'appui et vos axes de progression.
      </p>
    </div>
    """, unsafe_allow_html=True)

# ─── QUESTIONNAIRE ────────────────────────────────────────────────────────────
if not st.session_state.submitted:

    # Prénom
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        prenom = st.text_input("Prénom", placeholder="Votre prénom", label_visibility="visible")
    with col2:
        nom = st.text_input("Nom", placeholder="Votre nom", label_visibility="visible")
    with col3:
        date_val = st.date_input("Date", label_visibility="visible")

    st.markdown("""
    <div class="scale-legend">
      <div class="scale-item"><span>1</span>Pas du tout vrai</div>
      <div class="scale-item"><span>2</span>Rarement vrai</div>
      <div class="scale-item"><span>3</span>Parfois vrai</div>
      <div class="scale-item"><span>4</span>Souvent vrai</div>
      <div class="scale-item"><span>5</span>Tout à fait vrai</div>
    </div>
    """, unsafe_allow_html=True)

    q_global = 1
    all_answered = True

    with st.form("pentaptyque_form"):
        for dim_idx, (dim_name, dim_data) in enumerate(DIMENSIONS_DATA.items()):
            st.markdown(f"""
            <div class="dim-header">
              <div class="dim-num">Dimension {dim_idx+1} sur 5</div>
              <div class="dim-title">{dim_data['icon']} {dim_name.upper()}</div>
              <div class="dim-obj">{dim_data['objective']}</div>
            </div>
            """, unsafe_allow_html=True)

            for section_name, questions in dim_data["sections"].items():
                st.markdown(f'<div class="sub-section-title">{section_name}</div>', unsafe_allow_html=True)
                for q_text in questions:
                    key = f"q_{q_global}"
                    col_num, col_q, col_radio = st.columns([0.35, 3.5, 2])
                    with col_num:
                        st.markdown(f'<div class="q-num" style="padding-top:10px;">{q_global}.</div>', unsafe_allow_html=True)
                    with col_q:
                        st.markdown(
        f'<div style="font-size:17px;padding:16px 0;line-height:1.7;font-weight:500;color:#0f172a;">{q_text}</div>',
        unsafe_allow_html=True
    )
                    with col_radio:
                        val = st.radio(
                            label=f"q{q_global}",
                            options=[1, 2, 3, 4, 5],
                            index=2,
                            horizontal=True,
                            key=key,
                            label_visibility="collapsed"
                        )
                        st.session_state.answers[key] = val
                    st.divider()
                    q_global += 1

        # Progress indicator
        answered_count = len(st.session_state.answers)
        pct = int((answered_count / 125) * 100) if answered_count else 0

        st.markdown("<br/>", unsafe_allow_html=True)
        submitted = st.form_submit_button("⬡  ENVOYER MES RÉPONSES", use_container_width=True)

    if submitted:
    save_answers_to_csv(
        prenom=prenom,
        nom=nom,
        answers=st.session_state.answers,
        engagement=st.session_state.get("engagement", "")
    )
    st.success("Vos réponses ont bien été envoyées. Merci.")
    st.stop()

# ─── RESULTS ──────────────────────────────────────────────────────────────────
if mode == "Coach":
    prenom = st.session_state.get("prenom", "")
    nom = st.session_state.get("nom", "")

    # Hero results
    st.markdown(f"""
<div class="hero">
  <div class="subtitle">Résultats</div>
  <h1>VOTRE <span>PENTAPTYQUE</span></h1>
  <p>Analyse complète de vos 5 dimensions — <strong style="color:#0f172a;">{prenom} {nom}</strong></p>
</div>
""", unsafe_allow_html=True)

    # Calculate scores
    dims = list(DIMENSIONS_DATA.keys())
    scores_bruts = {d: 0 for d in dims}
    q_global = 1
    for dim_name, dim_data in DIMENSIONS_DATA.items():
        for section_name, questions in dim_data["sections"].items():
            for _ in questions:
                key = f"q_{q_global}"
                scores_bruts[dim_name] += st.session_state.answers.get(key, 3)
                q_global += 1
    scores_100 = {d: score_sur_100(s) for d, s in scores_bruts.items()}

    # ── RADAR ─────────────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    fig = go.Figure()
    theta = list(scores_100.keys()) + [list(scores_100.keys())[0]]
    r_vals = list(scores_100.values()) + [list(scores_100.values())[0]]

    fig.add_trace(go.Scatterpolar(
        r=r_vals,
        theta=theta,
        fill='toself',
        fillcolor='rgba(12,192,223,0.15)',
        line=dict(color='#0cc0df', width=2.5),
        marker=dict(color='#0cc0df', size=8),
        name='Profil',
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='white',
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color='#6b7280', size=9),
                gridcolor='#d1d5db',
                tickvals=[20, 40, 60, 80, 100],
                ticktext=['20', '40', '60', '80', '100'],
            ),
            angularaxis=dict(
                tickfont=dict(color='#374151', size=11, family='Barlow'),
                gridcolor='#d1d5db',
                linecolor='#d1d5db',
            ),
            gridshape='linear',
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#1f2933', family='Barlow'),
        margin=dict(t=40, b=40, l=60, r=60),
        height=420,
        showlegend=False,
    )
    # Add reference rings
    for level, color, label in [(60, '#f0a050', 'Zone à renforcer'), (80, '#0cc0df', "Zone d'appui")]:
        fig.add_trace(go.Scatterpolar(
            r=[level]*len(dims) + [level],
            theta=theta,
            mode='lines',
            line=dict(color=color, width=1, dash='dot'),
            name=label,
            showlegend=True,
        ))
    fig.update_layout(
        legend=dict(
            font=dict(color='#888', size=9),
            bgcolor='rgba(0,0,0,0)',
            x=0.5, y=-0.1, xanchor='center',
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── SCORES GRID ───────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (dim, score) in enumerate(scores_100.items()):
        level, level_label, level_color = get_level(score)
        with cols[i]:
            st.markdown(f"""
            <div style="background:white;padding:20px 12px;text-align:center;border-top:3px solid {level_color};box-shadow:0 4px 14px rgba(0,0,0,0.04);">
              <div style="font-size:9px;letter-spacing:2px;color:#6b7280;text-transform:uppercase;margin-bottom:8px;">{DIMENSIONS_DATA[dim]['icon']} {dim}</div>
              <div style="font-size:44px;font-weight:900;color:{level_color};font-family:'Barlow Condensed',sans-serif;line-height:1;">{score}</div>
              <div style="font-size:9px;color:#9ca3af;margin-top:4px;">/100</div>
              <div style="font-size:8px;letter-spacing:1px;color:{level_color};margin-top:8px;text-transform:uppercase;">{level_label.split(' ', 1)[1] if ' ' in level_label else level_label}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── DIMENSION BY DIMENSION ────────────────────────────────────────────
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#888;font-weight:700;border-bottom:2px solid #0a0a0a;padding-bottom:10px;margin-bottom:20px;">ANALYSE PAR DIMENSION</div>', unsafe_allow_html=True)

    for dim, score in scores_100.items():
        level, level_label, level_color = get_level(score)
        comment = COMMENTS[dim][level]
        card_class = {"high": "", "mid": " warn", "low": " danger"}[level]
        st.markdown(f"""
        <div class="result-card{card_class}">
          <div class="dim-name">{DIMENSIONS_DATA[dim]['icon']} {dim.upper()}</div>
          <div class="score-big">{score}<span style="font-size:14px;color:#555;">/100</span></div>
          <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:{level_color};margin:4px 0;">{level_label}</div>
          <div class="interp">{comment}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── CROSS READINGS ────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#888;font-weight:700;border-bottom:2px solid #0a0a0a;padding-bottom:10px;margin-bottom:20px;">LECTURES CROISÉES — INTERDÉPENDANCES</div>', unsafe_allow_html=True)

    cross_found = False
    S = scores_100

    crosses = [
        # Physique <> Mental
        (S["Physique"] < 60 and S["Mental"] >= 80, "danger",
         "🏃 Physique ↔ 🧠 Mental",
         "Physique faible + Mental fort : risque de sur-régime intellectuel. Réintroduire de la récupération corporelle et du relâchement."),
        (S["Physique"] >= 80 and S["Mental"] < 60, "warn",
         "🏃 Physique ↔ 🧠 Mental",
         "Corps solide mais direction mentale absente. Travail sur la structuration, l'objectif et la concentration."),

        # Physique <> Émotionnel
        (S["Physique"] < 60 and S["Émotionnel"] >= 60, "warn",
         "🏃 Physique ↔ 💓 Émotionnel",
         "Capacité émotionnelle préservée mais fatigue corporelle. Ralentir le rythme, travailler sur le relâchement."),
        (S["Physique"] < 60 and S["Émotionnel"] < 60, "danger",
         "🏃 Physique ↔ 💓 Émotionnel",
         "Épuisement physique et surcharge émotionnelle simultanés. Urgence de recentrage — accompagnement intégratif corps-esprit recommandé."),

        # Mental <> Émotionnel
        (S["Mental"] >= 80 and S["Émotionnel"] < 60, "warn",
         "🧠 Mental ↔ 💓 Émotionnel",
         "Hypercontrôle mental, faible connexion émotionnelle. Travailler l'écoute intérieure et la gestion des ressentis."),
        (S["Mental"] < 60 and S["Émotionnel"] >= 80, "warn",
         "🧠 Mental ↔ 💓 Émotionnel",
         "Sensibilité forte mais manque de structure cognitive. Structurer la pensée, canaliser l'émotion dans l'action."),

        # Sens <> Comportemental
        (S["Sens"] >= 80 and S["Comportemental"] < 60, "warn",
         "★ Sens ↔ ⬡ Comportemental",
         "Vision forte mais passage à l'action difficile — profil visionnaire non concrétiseur. Structurer la mise en mouvement et les rituels d'action."),
        (S["Sens"] < 60 and S["Comportemental"] >= 80, "warn",
         "★ Sens ↔ ⬡ Comportemental",
         "Action efficace sans cap clair. Reconnecter l'action à la finalité et au sens personnel."),

        # Mental <> Sens
        (S["Mental"] >= 80 and S["Sens"] < 60, "warn",
         "🧠 Mental ↔ ★ Sens",
         "Vision floue malgré un mental performant. Redonner du sens à la planification et clarifier la trajectoire."),

        # Émotionnel <> Sens
        (S["Émotionnel"] >= 80 and S["Sens"] < 60, "warn",
         "💓 Émotionnel ↔ ★ Sens",
         "Investissement affectif fort sans direction claire. Clarifier la mission pour canaliser l'énergie."),

        # Triptyques
        (S["Physique"] < 60 and S["Mental"] < 60 and S["Émotionnel"] < 60, "danger",
         "⚠ Triptyque Physique + Mental + Émotionnel",
         "Burn-out latent : tension continue, perte d'élan, désalignement global. Travail prioritaire de récupération et reconnexion au sens."),
        (S["Mental"] >= 80 and S["Comportemental"] >= 80 and S["Sens"] < 60, "warn",
         "⚠ Triptyque Mental + Comportemental + Sens",
         "Profil d'exécutant performant mais en perte de motivation. Reconnecter la mission à la direction personnelle."),
        (S["Sens"] >= 80 and S["Émotionnel"] >= 80 and S["Physique"] < 60, "warn",
         "⚠ Triptyque Sens + Émotionnel + Physique",
         "Engagement passionné, risque d'épuisement. Ramener la vision à un rythme soutenable."),
    ]

    for condition, cls, title, text in crosses:
        if condition:
            cross_found = True
            st.markdown(f"""
            <div class="cross-card {cls}">
              <strong>{title}</strong><br/>
              {text}
            </div>
            """, unsafe_allow_html=True)

    if not cross_found:
        st.markdown("""
        <div class="cross-card">
          <strong>✓ Profil équilibré</strong><br/>
          Aucune tension majeure entre dimensions détectée. Votre profil montre une cohérence globale. 
          Identifiez votre dimension la plus haute comme levier d'exemplarité et votre dimension 
          la plus basse comme axe de progression prioritaire.
        </div>
        """, unsafe_allow_html=True)

    # ── BAR CHART ─────────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    bar_colors = []
    for d in dims:
        lvl, _, _ = get_level(scores_100[d])
        bar_colors.append({"high": "#0cc0df", "mid": "#f0a050", "low": "#e05a5a"}[lvl])

    fig2 = go.Figure(go.Bar(
        x=dims,
        y=list(scores_100.values()),
        marker_color=bar_colors,
        text=[f"{v}/100" for v in scores_100.values()],
        textposition='outside',
        textfont=dict(color='white', size=11, family='Barlow'),
    ))
    fig2.add_hline(y=80, line_dash="dot", line_color="#0cc0df", line_width=1, annotation_text="Zone d'appui (80)", annotation_font_color="#0cc0df", annotation_font_size=9)
    fig2.add_hline(y=60, line_dash="dot", line_color="#f0a050", line_width=1, annotation_text="Zone à renforcer (60)", annotation_font_color="#f0a050", annotation_font_size=9)
    fig2.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#1f2933', family='Barlow'),
        xaxis=dict(tickfont=dict(color='#374151', size=11), gridcolor='#e5e7eb', linecolor='#d1d5db'),
        yaxis=dict(range=[0, 115], tickfont=dict(color='#6b7280', size=9), gridcolor='#e5e7eb', zerolinecolor='#d1d5db'),
        margin=dict(t=30, b=20, l=20, r=20),
        height=340,
        showlegend=False,
        bargap=0.35,
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── SYNTHÈSE COACHING ───────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#888;font-weight:700;border-bottom:2px solid #0a0a0a;padding-bottom:10px;margin-bottom:20px;">SYNTHÈSE COACHING</div>',
        unsafe_allow_html=True
    )

    moyenne_globale = round(sum(scores_100.values()) / len(scores_100))
    dimension_forte = max(scores_100, key=scores_100.get)
    dimension_fragile = min(scores_100, key=scores_100.get)

    pistes = {
        "Physique": "retrouver de l'énergie, améliorer la récupération et remettre du mouvement dans le quotidien",
        "Mental": "clarifier les priorités, alléger la charge mentale et renforcer le focus",
        "Émotionnel": "mieux réguler les tensions, identifier les déclencheurs émotionnels et renforcer la stabilité intérieure",
        "Sens": "retrouver du cap, réaligner les actions avec les valeurs et redonner de la perspective",
        "Comportemental": "transformer plus nettement les intentions en actions concrètes et installer des routines d'exécution",
    }

    st.markdown(f"""
    <div class="cross-card">
      <strong>Score global :</strong> {moyenne_globale}/100<br/>
      <strong>Dimension d'appui dominante :</strong> {dimension_forte} ({scores_100[dimension_forte]}/100)<br/>
      <strong>Dimension prioritaire à renforcer :</strong> {dimension_fragile} ({scores_100[dimension_fragile]}/100)
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cross-card warn">
      <strong>Hypothèse de travail prioritaire</strong><br/>
      La priorité actuelle semble être de <strong>{pistes[dimension_fragile]}</strong>.
    </div>
    """, unsafe_allow_html=True)

    engagement = st.text_area(
    "Premier engagement concret",
    placeholder="Ex : bloquer 2 créneaux de récupération par semaine, clarifier mes 3 priorités du mois, remettre du mouvement physique, retravailler mon cap...",
    height=120,
    key="engagement"
)

    if engagement:
        st.markdown(f"""
        <div class="cross-card">
          <strong>Engagement formulé</strong><br/>
          {engagement}
        </div>
        """, unsafe_allow_html=True)

    # ── EXPORT PDF ─────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#888;font-weight:700;border-bottom:2px solid #0a0a0a;padding-bottom:10px;margin-bottom:20px;">EXPORT</div>',
        unsafe_allow_html=True
    )

    filename = f"bilan_pentaptyque_{prenom}_{nom}.pdf".replace(" ", "_").replace("__", "_")

if st.session_state.pdf_ready is None:
    if st.button("⎙  PRÉPARER LE BILAN PDF", use_container_width=True):
        st.session_state.pdf_ready = build_pdf(
            prenom=prenom,
            nom=nom,
            scores_100=scores_100,
            dimension_forte=dimension_forte,
            dimension_fragile=dimension_fragile,
            moyenne_globale=moyenne_globale,
            engagement=engagement,
        )
        st.rerun()

if st.session_state.pdf_ready is not None:
    st.download_button(
        label="⬇  TÉLÉCHARGER LE BILAN PDF",
        data=st.session_state.pdf_ready,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
    )
    # ── RESET ─────────────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
if st.button("↩  RECOMMENCER UN NOUVEAU QUESTIONNAIRE"):
    st.session_state.submitted = False
    st.session_state.answers = {}
    st.session_state.pdf_ready = None
    st.rerun()

    st.markdown("""
    <div style="text-align:center;padding:32px 0 16px;font-size:9px;letter-spacing:3px;color:#555;text-transform:uppercase;">
        © REMATCH — Document confidentiel — rematch-coaching.com
    </div>
    """, unsafe_allow_html=True)
