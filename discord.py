import os
import requests
from dotenv import load_dotenv

load_dotenv()

class Discord:
    def __init__(self):
        self.client_id = os.getenv('DISCORD_ID')
        self.client_secret = os.getenv('DISCORD_SECRET')
        self.discord_token = os.getenv('DISCORD_TOKEN')
        self.API_ENDPOINT = 'https://discord.com/api/v10'
        self.discord_chanel_id = os.getenv('DISCORD_CHANEL_ID')
        self.headers = {
            'Authorization': f'Bot {self.discord_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    def post(self, message: str):
        if not self.discord_chanel_id or not self.discord_token:
            print("Pas de discord_chanel_id ou discord_token veuillez le noter dans le fichier .env")
            return None

        # Vérifier si l'image existe
        os.makedirs("img", exist_ok=True)
        IMAGE_PATH = "./img/hey.jpg"
        if not os.path.exists(IMAGE_PATH):
            print(f"L'image {IMAGE_PATH} n'existe pas!")
            return None

        # Important: Ne pas modifier le Content-Type pour les fichiers
        self.headers.pop('Content-Type', None)

        try:
            with open(IMAGE_PATH, 'rb') as image_file:
                files = {
                    'file': ('hey.jpg', image_file, 'image/jpeg')
                }
                
                payload = {
                    'content': message
                }

                r = requests.post(
                    f'{self.API_ENDPOINT}/channels/{self.discord_chanel_id}/messages',
                    headers=self.headers,
                    data=payload,
                    files=files
                )
                
                if r.status_code == 200:
                    print("Message et image envoyés avec succès!")
                    return r.json()
                else:
                    print(f"Erreur: {r.status_code}")
                    print(r.text)
                    return None
                    
        except Exception as e:
            print(f"Une erreur est survenue: {str(e)}")
            return None