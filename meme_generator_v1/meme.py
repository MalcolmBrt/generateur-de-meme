from dotenv import load_dotenv
import os
import requests
import random
from datetime import datetime
import pytz
from supabase import create_client
from PIL import ImageDraw, ImageFont

load_dotenv()
APIKEY_OPENROUTER = os.getenv("APIKEY_OPENROUTER")
USERNAME_IMGFLIP = os.getenv("USERNAME_IMGFLIP")
PASSWORD_IMGFLIP = os.getenv("PASSWORD_IMGFLIP")
URL_SUPABASE = os.getenv("URL_SUPABASE")
APIKEY_SUPABASE = os.getenv("APIKEY_SUPABASE")
supabase = create_client(URL_SUPABASE, APIKEY_SUPABASE)

class Meme:
    def __init__(self):
        self.model_captions = "anthropic/claude-3.5-haiku"
        self.model_title = "openai/gpt-4.1-nano"
        self.created_at = datetime.now(pytz.timezone("Pacific/Noumea"))
        self.template_id = None
        self.template_name = None
        self.template_url = None
        self.box_count = None
        self.captions = []
        self.title = None
        self.url = None

    def get_random_template(self):
        url = "https://api.imgflip.com/get_memes"
        response = requests.get(url)
        data = response.json()
        if data["success"]:
            memes = data["data"]["memes"]
            meme = random.choice(memes)
            self.template_id = meme["id"]
            self.template_name = meme["name"]
            self.template_url = meme["url"]
            self.box_count = meme["box_count"]
        else:
            raise Exception("Erreur lors de la récupération des mèmes : " + data.get("error_message", "inconnue"))

    def generate_captions(self, style="absurde"):
        url = "https://openrouter.ai/api/v1/chat/completions"
        prompt = f"""
        Tu es un générateur de mèmes drôles dans un style {style}.
        Ton objectif est de créer un texte percutant, humoristique et viral.

        - Contexte du mème : {self.template_name}
        - Génère {self.box_count} légendes (une par case)
        - Pas d’explications, ni ponctuation inutile
        - Pas d’emojis ni émoticônes
        - Chaque ligne = une légende

        Réponds uniquement avec les phrases générées, une par ligne.
        """

        headers = {
            "Authorization": f"Bearer {APIKEY_OPENROUTER}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_captions,
            "messages": [{"role": "system", "content": prompt}]
        }

        while True:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            try:
                raw_text = data["choices"][0]["message"]["content"]
                lignes = [ligne.strip() for ligne in raw_text.splitlines() if ligne.strip()]
                if len(lignes) == self.box_count:
                    self.captions = lignes
                    return
            except Exception:
                continue

            
    def generate_title(self):
        url = "https://openrouter.ai/api/v1/chat/completions"
        prompt = f"""
        Tu es un générateur de titres pour des mèmes internet au ton sarcastique, absurde ou ironique.
        Ton objectif est de créer une phrase percutante et drôle qui introduit ou résume le mème de manière efficace.
        Analyse les légendes suivantes, qui correspondent aux différentes cases du mème, et crée un titre original, drôle et accrocheur, dans le style typique des mèmes viraux.

        Légendes du mème :
        {self.captions}

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
            "model": self.model_title,
            "messages": [
                {
                "role": "system",
                "content": prompt
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        self.title = data["choices"][0]["message"]["content"].strip()

    def create_imgflip_meme(self):
        url = "https://api.imgflip.com/caption_image"
        
        # Paramètres de base
        payload = {
            "template_id": self.template_id,
            "username": USERNAME_IMGFLIP,
            "password": PASSWORD_IMGFLIP,
        }
        
        for i, caption in enumerate(self.captions):
            payload[f"boxes[{i}][text]"] = caption

        # Requête POST avec data form-encoded
        response = requests.post(url, data=payload)
        data = response.json()

        if data["success"]:
            self.url = data["data"]["url"]
        else:
            raise Exception("Erreur : " + data.get("error_message", "inconnue"))
        
    def save_to_supabase(self):
        data = {
            "created_at": self.created_at.isoformat(),
            "template_id": self.template_id,
            "template_name": self.template_name,
            "template_url": self.template_url,
            "box_count": self.box_count,
            "captions": self.captions,
            "title": self.title,
            "url": self.url
        }
        response = supabase.table("memes").insert(data).execute()
        return response.data
    
    def generate(self, image, top_text, bottom_text):
        draw = ImageDraw.Draw(image)
        font_path = "arial.ttf"  # Ou un autre fichier .ttf présent sur ta machine
        try:
            font = ImageFont.truetype(font_path, size=40)
        except:
            font = ImageFont.load_default()

        width, height = image.size
        draw.text((width/2, 10), top_text, fill="white", anchor="ma", font=font)
        draw.text((width/2, height - 60), bottom_text, fill="white", anchor="ma", font=font)
        return image

    @staticmethod
    def get_all():
        response = supabase.table("memes").select("*").execute()
        return response.data

    def create(self, style="absurde"):
        self.get_random_template()
        self.generate_captions(style=style)
        self.generate_title()
        self.create_imgflip_meme()
        self.save_to_supabase()
