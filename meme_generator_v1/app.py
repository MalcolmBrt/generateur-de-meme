import streamlit as st
from PIL import Image
from meme import Meme
import requests

st.set_page_config(page_title="Générateur de Mèmes", layout="centered")

menu = st.sidebar.radio("Menu", ["🏠 Accueil", "🎨 Générer un mème", "📜 Voir les mèmes enregistrés"])

# --- PAGE D'ACCUEIL ---
if menu == "🏠 Accueil":
    st.title("🧠 Générateur de Mèmes IA")
    st.markdown("""
    Bienvenue sur **Générateur de Mèmes IA** !  
    Crée des mèmes drôles, absurdes ou sarcastiques grâce à l’IA.  
    👉 Choisis une image ou laisse l’IA utiliser un template aléatoire.

    **Fonctionnalités :**
    - 🎨 Génération de mèmes avec IA
    - 🧠 Choix du style : absurde, sarcastique, etc.
    - ☁️ Stockage Supabase
    - 📥 Téléchargement et 🗑️ suppression
    """)

# --- PAGE DE GÉNÉRATION ---
elif menu == "🎨 Générer un mème":
    st.title("🎨 Générateur de Mèmes")

    uploaded_image = st.file_uploader("Choisissez une image (ou laissez vide pour un template aléatoire)", type=["jpg", "jpeg", "png"])
    top_text = st.text_input("Texte du haut")
    bottom_text = st.text_input("Texte du bas")

    style = st.selectbox("🎭 Choisissez un style de mème IA", [
        "absurde", "sarcastique", "ironique", "culture web"
    ])

    generator = Meme()

    if uploaded_image and st.button("✨ Générer le mème personnalisé"):
        image = Image.open(uploaded_image)
        meme = generator.generate(image, top_text, bottom_text)
        st.image(meme, caption="Votre mème personnalisé", use_column_width=True)

    elif not uploaded_image and st.button("🎲 Générer automatiquement avec IA"):
        generator.create(style=style)
        response = requests.get(generator.url)
        if response.status_code == 200:
            st.image(generator.url, caption=generator.title, use_column_width=True)
            st.download_button(
                label="📥 Télécharger le mème",
                data=response.content,
                file_name="meme.jpg",
                mime="image/jpeg"
            )

# --- PAGE DES MÈMES ENREGISTRÉS ---
elif menu == "📜 Voir les mèmes enregistrés":
    st.title("📜 Mèmes enregistrés")

    try:
        memes = Meme.get_all()
        if memes:
            for meme in memes[::-1]:
                st.subheader(meme['title'])
                st.image(meme['url'], caption=meme['template_name'], use_column_width=True)

                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("🗑️ Supprimer", key=meme['url']):
                        Meme.delete_by_url(meme['url'])  # Optionnel si tu ajoutes cette méthode
                        st.success("Mème supprimé.")
                        st.experimental_rerun()
                with col2:
                    response = requests.get(meme['url'])
                    if response.status_code == 200:
                        st.download_button(
                            label="📥 Télécharger",
                            data=response.content,
                            file_name=f"{meme['title']}.jpg",
                            mime="image/jpeg",
                            key=meme['template_id'] + "_dl"
                        )

                st.markdown("---")
        else:
            st.info("Aucun mème enregistré pour le moment.")
    except Exception as e:
        st.error(f"Erreur : {str(e)}")
