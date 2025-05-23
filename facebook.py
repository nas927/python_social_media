import requests
import os
import string
import random
import webbrowser
from dotenv import load_dotenv

load_dotenv()

class Facebook:
    def __init__(self):
        self.client_id: str = os.getenv("FACEBOOK_CLIENT_ID")
        self.client_secret: str = os.getenv("FACEBOOK_CLIENT_SECRET")
        self.redirect_uri: str = os.getenv("CODE_URI")
        self.code: str = os.getenv("FACEBOOK_CODE")
        self.access_token: str = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.error = "Quelque chose s'est mal passée veuillez retenter !"
        
    def write_token_to_env(self, token_name: str, token_value:str ):
        # Écrire le token dans le fichier .env
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'r') as file:
            lines = file.readlines()
    
        access_token_line = f"{token_name}={token_value}\n"
        token_found = False
        
        for i, line in enumerate(lines):
            if line.startswith(f'{token_name}='):
                lines[i] = access_token_line
                token_found = True
                break
                
        if not token_found:
            lines.append(access_token_line)
            
        with open(env_path, 'w') as file:
            file.writelines(lines)
            
        print("Token écrit !")
        
    def get_auth_code(self):
        state: str = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        url: str = "https://www.facebook.com/v22.0/dialog/oauth?"
        
        data: str = (
            f"client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state}"
            f"&scope=business_management,pages_read_engagement,pages_manage_metadata,pages_read_user_content,"
            "pages_manage_posts,pages_manage_engagement,"
            "instagram_basic, instagram_content_publish"
        )
        
        full_url: str = url + data
        print(full_url)
        webbrowser.open(full_url)
        
    def get_access_token(self):
        if not self.code:
            print("Vous n'avez pas de code !")
            self.get_auth_code()
            return
        uri: str = "https://graph.facebook.com/v22.0/oauth/access_token?"
        
        data: str = (
            f"client_id={self.client_id}"
            f"&client_secret={self.client_secret}"
            f"&redirect_uri={self.redirect_uri}"
            f"&code={self.code}"
        )
        
        r = requests.get(uri + data)
        if r.status_code <= 300:
            r = r.json()
            if (r.get("access_token")):
                self.access_token = r["access_token"]
                self.write_token_to_env("FACEBOOK_ACCESS_TOKEN", self.access_token)
            print(r)
        else:
            print("Il y a un problème avec votre code vérifiez et réessayez")
            self.get_auth_code()
            print(r.text)
        return 
    
    def getId(self) -> bool | str:
        if not self.access_token:
            print("Il vous manque une token d'accès")
            self.get_access_token()
        
        r = requests.get(f"https://graph.facebook.com/v22.0/me?fields=id,name&access_token={self.access_token}")
        
        if (r.status_code <= 300):
            r = r.json()
            print(r)
            if (r.get("id")):
                return r["id"]
            
        else:
            print(self.error)
            print("https://developers.facebook.com/tools/explorer?method=GET&path=me%3Ffields%3Did%2Cname&version=v22.0")
            self.get_access_token()
            print(r.json())
        return False
        
    def get_page_id(self) -> str | bool:
        user_id: str | False = self.getId()
        
        if not user_id:
            self.get_access_token()
            return False
        
        uri: str = f"https://graph.facebook.com/v22.0/{user_id}/accounts?"
        data = "access_token=" + self.access_token
        
        r = requests.get(uri + data)
        if (r.status_code <= 300):
            r = r.json()
            print(r)
            if (r.get("data")[0]):
                r = r["data"][0]
                self.write_token_to_env("FACEBOOK_PAGE_ID", r["id"])
                return r["id"], r["access_token"]
        else:
            print(self.error)
            print(r.text)
        return False
    
    def upload_init(self) -> str | bool:
        if not self.client_id:
            print("Vous n'avez pas d'id de app important pour l'importation d'image")
            return
        elif not self.access_token:
            self.get_access_token()
            return
        
        file_path: str = "./img/hey.jpg"
        file_size: int = os.path.getsize(file_path)
        
        uri: str = f"https://graph.facebook.com/v22.0/{self.client_id}/uploads"
        headers: dict[str, str] = {
            "Content-Type": "image/jpg"
        }
        data: dict[str, str | int] = {
            "file_name": "hey.jpg",
            "file_length": file_size,
            "file_type": "image/jpg",
            "access_token": self.access_token
        }
        
        r = requests.post(uri, data=data, headers=headers)
        
        if (r.status_code <= 300):
            r = r.json()
            if (r.get("id")):
                return r["id"]
            print(r)
        else:
            print(self.error)
            print(r.text)
        return False
    
    def upload(self) -> str | bool:
        """Upload une photo vers Facebook en utilisant l'API correcte"""
        # Vérifier les prérequis
        if not self.access_token:
            print("Vous n'avez pas d'access token")
            self.get_access_token()
            return False
            
        # Récupérer le page_id et le token de la page
        page_data = self.get_page_id()
        if not page_data:
            return False
        
        page_id, page_access_token = page_data
        
        # Préparer le fichier
        file_path: str = "./img/hey.jpg"
        if not os.path.exists(file_path):
            print(f"L'image {file_path} n'existe pas!")
            return False

        # Upload l'image directement sur la page
        uri: str = f"https://graph.facebook.com/v22.0/{page_id}/photos"
        
        try:
            with open(file_path, 'rb') as image:
                files = {
                    'source': image
                }
                params = {
                    'access_token': page_access_token,
                    'published': 'false' 
                }
                
                r = requests.post(uri, files=files, data=params)
                
                if r.status_code <= 300:
                    response_data = r.json()
                    print("Photo uploadée avec succès!")
                    print(response_data)
                    if response_data.get('id'):
                        return response_data['id']
                else:
                    print(f"Erreur lors de l'upload: {r.status_code}")
                    print(r.text)
                    
        except Exception as e:
            print(f"Erreur lors de l'upload: {str(e)}")
        
        return False
    
    def post(self, message: str):
        """Publie un message avec une photo"""
        # Upload la photo d'abord
        photo_id = self.upload()
        if not photo_id:
            print("L'upload de la photo a échoué")
            return
            
        # Récupérer les infos de la page
        page_data = self.get_page_id()
        if not page_data:
            return
        
        page_id, page_access_token = page_data
        
        # Créer le post avec la photo
        uri: str = f"https://graph.facebook.com/v22.0/{page_id}/feed"
        data = {
            "message": message,
            "attached_media[0]": f"{{'media_fbid':'{photo_id}'}}",
            "access_token": page_access_token
        }
        
        r = requests.post(uri, data=data)
        
        if r.status_code <= 300:
            print("Publication réussie!")
            print(r.json())
        else:
            print(f"Erreur lors de la publication: {r.status_code}")
            print(r.text) 