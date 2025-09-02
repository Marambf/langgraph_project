import streamlit as st
from PIL import Image
from nodes import run_query_direct, create_agent_executor
import streamlit.components.v1 as components
import re
import os
from translate import detect_and_translate_to_english, translate_from_english

# Configuration de la page
st.set_page_config(page_title="STAC & Fire Chatbot", layout="centered")

# Logo
logo = Image.open("metaplanet_sas_logo.jpeg")
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(logo, width=150)
st.markdown("</div>", unsafe_allow_html=True)

# Titre
st.title("🛰️🔥 Metaplanet Earth Agent")

# Input utilisateur
user_input = st.text_input("📥 Entrez votre requête :")

# Initialiser l’agent une seule fois
if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = create_agent_executor()
agent_executor = st.session_state.agent_executor

# Stocker le dernier résultat pour éviter réexécution
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# Détection si c’est une requête satellite
def is_satellite_query(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in ["sentinel", "modis", "viirs", "ndvi", "stac"])

# Fonction traduction + traitement agent
def translate_query_and_response(user_input: str, agent):
    english_input, detected_lang = detect_and_translate_to_english(user_input)
    response = agent.invoke({"input": english_input})
    if isinstance(response, dict):
        output_text = response.get("output", str(response))
    else:
        output_text = str(response)
    return translate_from_english(output_text, detected_lang)

# Extraction des noms de fichiers HTML
def extract_all_html_filenames(text: str):
    return re.findall(r'([\w\-]+\.html)', text)

# Affichage d’un fichier HTML
def display_html_file(filename: str):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=600, width=800)
    else:
        st.warning(f"⚠️ Le fichier HTML `{filename}` n'existe pas.")

# Affichage de tous les HTML détectés
def display_all_html_from_text(text: str):
    filenames_in_text = extract_all_html_filenames(text)
    all_html_files = [f for f in os.listdir(".") if f.endswith(".html")]

    for name in filenames_in_text:
        if name in all_html_files:
            st.write(f"### Affichage de `{name}` :")
            display_html_file(name)
        else:
            possible_matches = [f for f in all_html_files if name.split("_")[-1] in f]
            if possible_matches:
                st.write(f"### Nom dans le texte `{name}` introuvable. Affichage du fichier similaire `{possible_matches[0]}` :")
                display_html_file(possible_matches[0])
            else:
                st.warning(f"⚠️ Aucun fichier HTML correspondant à `{name}` n'a été trouvé.")

# Bouton exécution
if st.button("🔍 Rechercher") and user_input:
    with st.spinner("⏳ Traitement de la requête..."):
        try:
            if is_satellite_query(user_input):
                result = run_query_direct(user_input)
            else:
                result = translate_query_and_response(user_input, agent_executor)

            st.session_state.last_result = result  # 🔑 Sauvegarde résultat
            st.success("✅ Requête traitée avec succès !")

        except Exception as e:
            st.error(f"❌ Erreur lors du traitement : {str(e)}")

# Affichage unique du dernier résultat (évite re-exécution)
if st.session_state.last_result:
    result = st.session_state.last_result

    # Cas 1 : Résultat avec images satellites
    if isinstance(result, dict) and "images" in result:
        st.write(f"### Résultats pour la collection `{result.get('collection', 'inconnue')}` :")
        for img in result["images"]:
            cloud = img.get("cloud_cover", "N/A")
            caption = f"📅 {img['date']} | ☁️ Nuage: {cloud:.2f}%" if isinstance(cloud, (int, float)) else f"📅 {img['date']} | ☁️ Nuage: {cloud}"
            st.image(img.get("thumbnail", ""), caption=caption, width=300)

    # Cas 2 : Résultat contenant une carte Folium
    elif isinstance(result, dict) and "folium_map" in result:
        st.write("### Carte générée :")
        folium_map = result["folium_map"]
        if hasattr(folium_map, "get_root"):
            html = folium_map.get_root().render()
            components.html(html, height=600)
        else:
            st.warning("⚠️ La carte ne peut pas être rendue correctement.")

    # Cas 3 : Texte contenant un fichier HTML
    elif isinstance(result, str) and (result.endswith(".html") or ".html" in result):
        st.write("### Résultat :")
        st.write(result)
        display_all_html_from_text(result)

    # Cas 4 : Autres résultats
    else:
        st.write("### Résultat :")
        st.write(result)
