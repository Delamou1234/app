# Application Streamlit : téléversement PDF -> extraction texte -> téléchargeable en .txt et .json
# Commentaires en français pour comprendre chaque étape

import io
import json
import streamlit as st
from PyPDF2 import PdfReader

st.set_page_config(page_title="PDF → TXT / JSON", layout="wide")
st.title("Convertisseur PDF → TXT / JSON")
st.markdown("Téléversez un fichier PDF. L'application extrait le texte de chaque page et vous permet de télécharger le résultat en .txt et en .json.")

# Zone de téléversement (côté barre latérale pour garder la zone principale propre)
st.sidebar.header("Importer un PDF")
uploaded_file = st.sidebar.file_uploader("Choisir un fichier PDF", type=["pdf"])

# Option : afficher plus ou moins de contenu dans l'aperçu
preview_chars = st.sidebar.number_input("Nombre de caractères pour l'aperçu (par page)", min_value=100, max_value=20000, value=1000, step=100)

if not uploaded_file:
    st.info("Téléversez un fichier PDF via la barre latérale pour commencer.")
    st.stop()

# Lire les bytes du fichier téléversé une seule fois
pdf_bytes = uploaded_file.read()

# Utiliser PyPDF2 pour lire le PDF depuis les bytes
try:
    reader = PdfReader(io.BytesIO(pdf_bytes))
except Exception as e:
    st.error(f"Impossible de lire le PDF : {e}")
    st.stop()

# Extraire le texte page par page
pages = []
for i, page in enumerate(reader.pages):
    try:
        text = page.extract_text()
    except Exception:
        text = None
    # Assurer une chaîne vide si None
    if not text:
        text = ""
    pages.append({"page_number": i + 1, "text": text})

# Construire le contenu TXT (séparateurs entre pages pour lisibilité)
txt_parts = []
for p in pages:
    txt_parts.append(f"=== Page {p['page_number']} ===\n{p['text']}")
txt_content = "\n\n".join(txt_parts)

# Construire le contenu JSON : métadonnées + pages
json_obj = {
    "filename": uploaded_file.name,
    "n_pages": len(pages),
    "pages": pages
}
json_content = json.dumps(json_obj, ensure_ascii=False, indent=2)

# Afficher résumé et aperçus
st.header("Résumé du fichier")
st.write(f"Nom du fichier : **{uploaded_file.name}**")
st.write(f"Nombre de pages : **{len(pages)}**")
total_chars = sum(len(p["text"]) for p in pages)
st.write(f"Nombre total de caractères extraits : **{total_chars}**")

st.header("Aperçu du texte par page")
for p in pages:
    with st.expander(f"Page {p['page_number']} — {min(len(p['text']), preview_chars)} caractères affichés"):
        # Afficher un aperçu limité pour éviter de surcharger l'interface
        st.write(p["text"][:preview_chars] + ("..." if len(p["text"]) > preview_chars else ""))

# Boutons de téléchargement : convertir en bytes pour st.download_button
txt_bytes = txt_content.encode("utf-8")
json_bytes = json_content.encode("utf-8")

st.header("Téléchargements")
col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="Télécharger (.txt)",
        data=txt_bytes,
        file_name=f"{uploaded_file.name.rsplit('.',1)[0]}.txt",
        mime="text/plain"
    )
with col2:
    st.download_button(
        label="Télécharger (.json)",
        data=json_bytes,
        file_name=f"{uploaded_file.name.rsplit('.',1)[0]}.json",
        mime="application/json"
    )

# Remarques et limitations
st.markdown("""
**Remarques :**
- L'extraction de texte fonctionne bien pour les PDFs contenant du texte numérique.
- Les PDFs scannés (images) nécessitent de l'OCR (p.ex. pytesseract) — fonctionnalité non incluse ici.
- Si l'extraction renvoie peu ou pas de texte, essayez d'ouvrir le PDF dans un lecteur pour vérifier s'il contient du texte sélectionnable.
""")