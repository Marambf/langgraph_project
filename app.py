import streamlit as st
from nodes import run_query_direct, create_agent_executor,translate_query_and_response
from PIL import Image

agent_executor = create_agent_executor()

logo = Image.open("metaplanet_sas_logo.jpeg")
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(logo, width=150)
st.markdown("</div>", unsafe_allow_html=True)

st.set_page_config(page_title="STAC Explorer", layout="centered")
st.title("🛰️ Metaplanet Chatbot")

user_input = st.text_input("📥 Entrez votre requête ")

def is_satellite_query(text: str) -> bool:
    return "sentinel" in text.lower() or "modis" in text.lower() or "viirs" in text.lower()

if st.button("🔍 Rechercher") and user_input:
    with st.spinner("Recherche en cours..."):
        try:
            if is_satellite_query(user_input):
                result = run_query_direct(user_input)
            else:
                response = translate_query_and_response(user_input, agent_executor, translate)
                result = response["output"]

                if "output" in response:
                    result = response["output"]
                else:
                    steps = response.get("intermediate_steps", [])
                    if steps:
                        last_observation = steps[-1][1]
                        result = last_observation
                    else:
                        result = "❌ Aucun résultat."

            st.success("✅ Requête traitée !")

            if isinstance(result, dict) and "images" in result:
                st.write(f"### Résultats pour la collection `{result['collection']}` :")
                for img in result["images"]:
                    cloud = img.get("cloud_cover", "N/A")
                    caption = f"📅 {img['date']} | ☁️ Cloud cover: {cloud:.2f}%" if isinstance(cloud, (int, float)) else f"📅 {img['date']} | ☁️ Cloud cover: {cloud}"
                    st.image(img.get("thumbnail", ""), caption=caption, width=300)

            else:
                st.write(result)

        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")

