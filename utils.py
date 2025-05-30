from dotenv import load_dotenv
import os
import requests
import random

load_dotenv()
APIKEY_OPENROUTER = os.getenv("APIKEY_OPENROUTER")
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

def generer_legendes(model, nombre_cases, description):
    url = "https://openrouter.ai/api/v1/chat/completions"
    prompt = f"""
        Tu es un générateur de mèmes drôles, au ton sarcastique, absurde ou ironique selon le contexte.
        Ton objectif est de créer un texte percutant et humoristique qui pourrait apparaître sur un mème internet viral.
        Génère un texte en {nombre_cases} phrases courtes, dans le style des mèmes classiques (format image avec texte).
        Utilise des expressions familières, des punchlines ou des références à la culture web si pertinent.
        Contexte du mème : {description}

        Contraintes :
        - Chaque phrase doit être indépendante et pouvoir figurer seule sur une case d'un mème (bulle ou zone de texte).
        - Utilise un ton drôle, absurde, ou sarcastique, selon ce qui est le plus adapté au contexte.
        - N'inclus pas d'explication ou de commentaire hors mème.

        Réponds uniquement par les phrases générées, séparées par un simple retour à la ligne, sans lignes vides ni espaces superflus au début ou à la fin des phrases.
        """ 
    headers = {
    "Authorization": f"Bearer {APIKEY_OPENROUTER}",
    "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {
            "role": "system",
            "content": prompt
            }
        ]
    }
    
    while True:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        try:
            raw_text = data["choices"][0]["message"]["content"]
            lignes = [ligne.strip() for ligne in raw_text.splitlines() if ligne.strip()]
            if len(lignes) == nombre_cases:
                return lignes
        except Exception:
            continue  # Recommence silencieusement si une erreur survient
        
def generer_titre(model, legendes):
    url = "https://openrouter.ai/api/v1/chat/completions"
    prompt = f"""
    Tu es un générateur de titres pour des mèmes internet au ton sarcastique, absurde ou ironique.
    Ton objectif est de créer une phrase percutante et drôle qui introduit ou résume le mème de manière efficace.
    Analyse les légendes suivantes, qui correspondent aux différentes cases du mème, et crée un titre original, drôle et accrocheur, dans le style typique des mèmes viraux.

    Légendes du mème :
    {legendes}

    Contraintes :
    - Le titre doit être court, mémorable et immédiatement compréhensible.
    - Il peut être absurde, ironique, familier ou référencer une situation web connue.
    - Ne reformule pas simplement les légendes : propose un nouvel angle humoristique qui donne envie de lire le mème.
    - Réponds uniquement avec le titre, sans explication ni ponctuation superflue.
    """
    headers = {
    "Authorization": f"Bearer {APIKEY_OPENROUTER}",
    "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {
            "role": "system",
            "content": prompt
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()



def generer_meme_imgflip(template_id, legendes):
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
    
def creer_meme():
    meme=recuperer_random_meme()
    legendes=generer_legendes("anthropic/claude-3.5-haiku", meme["box_count"], meme["name"])
    titre=generer_titre("openai/gpt-4.1-nano", legendes)
    memeimgflip=generer_meme_imgflip(meme["id"], legendes)
    return (titre, memeimgflip)