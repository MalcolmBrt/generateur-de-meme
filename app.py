import streamlit as st
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

# def recuperer_meme():
    

def generer_legendes(nombre_cases, description):
    load_dotenv()
    client = genai.Client(
        api_key=os.getenv("GOOGLEAISTUDIO_APIKEY"),
    )
    
    prompt = f"""
        Tu es un générateur de mèmes drôles, au ton sarcastique, absurde ou ironique selon le contexte. Ton objectif est de créer un texte percutant et humoristique qui pourrait apparaître sur un mème internet viral.
        Génère un texte en {nombre_cases} phrases courtes, dans le style des mèmes classiques (format image avec texte). Utilise des expressions familières, des punchlines ou des références à la culture web si pertinent.
        Contexte du mème : {description}

        Contraintes :
        - Chaque phrase doit être indépendante et pouvoir figurer seule sur une case d'un mème (bulle ou zone de texte).
        - Utilise un ton drôle, absurde, ou sarcastique, selon ce qui est le plus adapté au contexte.
        - N'inclus pas d'explication ou de commentaire hors mème.

        Réponds uniquement par les phrases générées, sans aucun texte en plus.
        """

    model = "gemini-2.5-flash-preview-05-20"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")
