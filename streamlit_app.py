# streamlit_app.py
import streamlit as st
from PIL import Image
from nodes import run_query_direct, create_agent_executor
import streamlit.components.v1 as components
import re
import os

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

# Initialiser l’agent (une seule fois au lancement)
if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = create_agent_executor()

agent_executor = st.session_state.agent_executor

# Détecter si la requête est purement satellite
def is_satellite_query(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in ["sentinel", "modis", "viirs", "ndvi", "stac"])

# Fonction traduisant et traitant la requête via l'agent
def translate_query_and_response(user_input: str, agent):
    response = agent.invoke({"input": user_input})
    if isinstance(response, dict):
        return response.get("output", str(response))
    return str(response)

# Extraction du nom du fichier HTML depuis un texte
def extract_html_filename(text: str) -> str:
    match = re.search(r'([\w\-]+\.html)', text)
    return match.group(1) if match else ""

# Affichage de fichier HTML si existe
def display_html_file(filename: str):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=600, width=900)

    else:
        st.warning(f"⚠️ Le fichier HTML `{filename}` n'existe pas.")

# Bouton de recherche
if st.button("🔍 Rechercher") and user_input:
    with st.spinner("⏳ Traitement de la requête..."):
        try:
            if is_satellite_query(user_input):
                result = run_query_direct(user_input)
            else:
                result = translate_query_and_response(user_input, agent_executor)

            st.success("✅ Requête traitée avec succès !")

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

            # Cas 3 : Texte contenant une référence à un fichier HTML
            elif isinstance(result, str) and result.endswith(".html") or ".html" in result:
                st.write("### Résultat :")
                st.write(result)

                # Extraire le nom du fichier HTML
                filename = extract_html_filename(result)
                if filename:
                    display_html_file(filename)
                else:
                    st.warning("⚠️ Aucun fichier HTML trouvé dans le texte.")

            # Cas 4 : Autres résultats
            else:
                st.write("### Résultat :")
                st.write(result)

        except Exception as e:
            st.error(f"❌ Erreur lors du traitement : {str(e)}")
