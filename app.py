import streamlit as st
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import requests
import random

load_dotenv()
APIKEY_GOOGLEAISTUDIO = os.getenv("APIKEY_GOOGLEAISTUDIO")
USERNAME_IMGFLIP = os.getenv("USERNAME_IMGFLIP")
PASSWORD_IMGFLIP = os.getenv("PASSWORD_IMGFLIP")


def recuperer_random_meme():
    url = "https://api.imgflip.com/get_memes"
    response = requests.get(url)
    data = response.json()
    if data["success"]:
        memes = data["data"]["memes"]
        meme = random.choice(memes)
        return meme
    else:
        raise Exception("Erreur lors de la récupération des mèmes : " + data.get("error_message", "inconnue"))

def generer_legendes(nombre_cases, description):
    client = genai.Client(
        api_key=APIKEY_GOOGLEAISTUDIO,
    )
    
    prompt = f"""
        Tu es un générateur de mèmes drôles, au ton sarcastique, absurde ou ironique selon le contexte. Ton objectif est de créer un texte percutant et humoristique qui pourrait apparaître sur un mème internet viral.
        Génère un texte en {nombre_cases} phrases courtes, dans le style des mèmes classiques (format image avec texte). Utilise des expressions familières, des punchlines ou des références à la culture web si pertinent.
        Contexte du mème : {description}

        Contraintes :
        - Chaque phrase doit être indépendante et pouvoir figurer seule sur une case d'un mème (bulle ou zone de texte).
        - Utilise un ton drôle, absurde, ou sarcastique, selon ce qui est le plus adapté au contexte.
        - N'inclus pas d'explication ou de commentaire hors mème.

        Réponds uniquement par les phrases générées, séparées par un simple retour à la ligne, sans lignes vides ni espaces superflus au début ou à la fin des phrases.
        """

    model = "gemini-2.5-flash-preview-05-20"
    
    while True:
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
        
        legendes = []
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            legendes.extend(chunk.text.splitlines())
            
        # Nettoyage
        legendes = [ligne.strip() for ligne in legendes if ligne.strip()]

        if len(legendes) == nombre_cases:
            return legendes
        # Sinon, on boucle automatiquement jusqu'à ce que ce soit bon


def generer_meme(template_id, legendes):
    url = "https://api.imgflip.com/caption_image"
    
    # Paramètres de base
    payload = {
        "template_id": template_id,
        "username": USERNAME_IMGFLIP,
        "password": PASSWORD_IMGFLIP,
    }
    
    for i, legende in enumerate(legendes):
        payload[f"boxes[{i}][text]"] = legende

    # Requête POST avec data form-encoded
    response = requests.post(url, data=payload)
    data = response.json()

    if data["success"]:
        return data["data"]["url"]
    else:
        raise Exception("Erreur : " + data.get("error_message", "inconnue"))

    


if __name__=="__main__":
    meme=recuperer_random_meme()
    print(meme)
    legendes=generer_legendes(meme["box_count"], meme["name"])
    print(legendes)
    newmeme=generer_meme(meme["id"], legendes)
    print(newmeme)
    