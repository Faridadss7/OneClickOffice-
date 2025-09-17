# main.py
import streamlit as st
import pandas as pd
from templates import TABLEAU_TEMPLATES, FLYER_TEMPLATES
from mini_ia import check_missing_columns, find_empty_cells, suggest_columns_from_phrase
from export_utils import df_to_excel_bytes, df_to_png_bytes, df_table_and_chart_to_pdf_bytes, generate_flyer_pdf_bytes
from datetime import datetime

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

st.set_page_config(page_title="OneClickOffice — Tableaux & Flyers", layout="wide")
st.title("🖱️ OneClickOffice — Tout-en-un (Tableaux, Graphiques, Flyers)")

# Sidebar configuration
st.sidebar.header("Configuration")
choice = st.sidebar.selectbox("Template", ["Ventes","Comptabilité","Suivi médical","Emploi du temps","Secrétariat","Personnalisé"])
suggest_phrase = st.sidebar.text_input("Décris brièvement ce que tu veux (facultatif)", "")

if choice != "Personnalisé":
    default_cols = TABLEAU_TEMPLATES.get(choice, ["Nom","Valeur"])
else:
    default_cols = st.sidebar.text_input("Entrez les colonnes séparées par une virgule", value="Nom, Valeur").split(",")

# Mini-IA suggestion
if suggest_phrase:
    suggested = suggest_columns_from_phrase(suggest_phrase)
else:
    suggested = []

cols_input = st.sidebar.text_input("Colonnes (séparées par ,)", value=",".join([c.strip() for c in default_cols]))
cols = [c.strip() for c in cols_input.split(",") if c.strip()]

st.sidebar.markdown("---")
n_rows = st.sidebar.number_input("Lignes initiales", min_value=0, max_value=200, value=3, step=1)
upload = st.sidebar.file_uploader("Importer CSV (optionnel)", type=["csv"])

# Construction du dataframe initial
if upload:
    df = pd.read_csv(upload)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols]
else:
    df = pd.DataFrame([[""]*len(cols) for _ in range(n_rows)], columns=cols)

# Mini-IA avertissements
missing = check_missing_columns(choice, cols) if choice != "Personnalisé" else []
if missing:
    st.sidebar.warning(f"Colonnes manquantes selon template {choice}: {', '.join(missing)}")
if suggested:
    st.sidebar.info(f"Suggestions de colonnes (d'après ta phrase) : {', '.join(suggested)}")

st.subheader("1) Édition du tableau")
edited = st. data_editor(df, num_rows="dynamic")
df = edited.copy()

# Détection des colonnes numériques
for c in df.columns:
    if any(k in c.lower() for k in ["quant", "prix", "montant", "total", "valeur"]):
        df[c] = pd.to_numeric(df[c], errors="coerce")

empties = find_empty_cells(df)
if empties:
    st.warning(f"Attention : valeurs vides détectées -> {empties}")

st.subheader("2) Graphique (choisis colonnes)")
numeric_cols = df.select_dtypes(include="number").columns.tolist()
label_cols = [c for c in df.columns if c not in numeric_cols]
st.write("Colonnes numériques détectées :", numeric_cols)
chart_type = st.selectbox("Type de graphique", ["Barres","Ligne","Camembert"])
value_col = st.selectbox("Colonne à tracer (valeur)", options=numeric_cols if numeric_cols else df.columns.tolist())
label_col = st.selectbox("Colonne pour labels (optionnel)", options=[""] + df.columns.tolist())
label_col = label_col if label_col != "" else None
chart_title = st.text_input("Titre du graphique", value=f"{value_col} - graphique")

if st.button("Générer aperçu graphique"):
    try:
        png_buf = df_to_png_bytes(df, x_col=label_col, y_col=value_col, chart_type=chart_type, title=chart_title)
        st.image(png_buf)
        st.success("Aperçu graphique généré")
    except Exception as e:
        st.error(f"Erreur génération graphique : {e}")

st.subheader("3) Export (Excel, PDF, Flyer)")
base_name = f"OneClickOffice_{choice.replace(' ','_')}_{timestamp()}"

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Exporter Excel"):
        excel_buf = df_to_excel_bytes(df)
        st.download_button("Télécharger Excel", data=excel_buf, file_name=f"{base_name}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with col2:
    if st.button("Exporter PDF (tableau + graphique)"):
        png_buf = None
        try:
            png_buf = df_to_png_bytes(df, x_col=label_col, y_col=value_col, chart_type=chart_type, title=chart_title)
        except:
            png_buf = None
        pdf_buf = df_table_and_chart_to_pdf_bytes(df, png_bytes=png_buf, title=f"OneClickOffice - {choice} - {chart_title}")
        st.download_button("Télécharger PDF", data=pdf_buf, file_name=f"{base_name}.pdf", mime="application/pdf")

with col3:
    if st.button("Exporter flyer simple (PDF)"):
        lines = []
        lines.append(st.text_input("Titre du flyer", value=f"Événement {choice}"))
        lines.append(st.text_input("Slogan / détail 1", value="Détail..."))
        lines.append(st.text_input("Détail 2 (date/lieu)", value="Date - Lieu"))
        bg_color = st.selectbox("Couleur de fond", options=[v["background_color"] for v in FLYER_TEMPLATES.values()])
        flyer_buf = generate_flyer_pdf_bytes([l for l in lines if l], bg_color=bg_color, title=lines[0] or "OneClickOffice Flyer")
        st.download_button("Télécharger Flyer PDF", data=flyer_buf, file_name=f"OneClickOffice_flyer_{timestamp()}.pdf", mime="application/pdf")

st.write(" Astuce : Créé un petit tableau d'abord puis augmente les lignes.")