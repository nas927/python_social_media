# Don't forget requirement.txt 
# cd thisfolder 
# pip install -r requirement.txt
# Python 3.12.6
import requests
import bot
import os
import random
import string
import webbrowser
from dotenv import load_dotenv

load_dotenv()

class Linkedin:
    
    def __init__(self):
        self.image: str = os.getenv('IMAGE')
        self.message: str = os.getenv('MESSAGE')
        self._code: str = os.getenv('LINKEDIN_CODE')
        self._client_id: str = os.getenv('LINKEDIN_CLIENT_ID')
        self._client_secret: str = os.getenv('LINKEDIN_CLIENT_SECRET')
        self._redirect: str = os.getenv('CODE_URI')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.headers: dict = {
            "X-Restli-Protocol-Version": "2.0.0",
            "Connection": "Keep-Alive",
            "Authorization": f"Bearer {self.access_token}",
            'Content-Type': 'application/json'
        }
    
    def write_token_to_env(self):
        # Écrire le token dans le fichier .env
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'r') as file:
            lines = file.readlines()
    
        access_token_line = f"LINKEDIN_ACCESS_TOKEN={self.access_token}\n"
        token_found = False
        
        for i, line in enumerate(lines):
            if line.startswith('LINKEDIN_ACCESS_TOKEN='):
                lines[i] = access_token_line
                token_found = True
                break
                
        if not token_found:
            lines.append(access_token_line)
            
        with open(env_path, 'w') as file:
            file.writelines(lines)
            
        print("Token écrit !")
        
    # dont use this function unless you are really sure what you do 
    def open_url_access(self) -> dict:
        state: str = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        auth_url: str = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={self._client_id}&redirect_uri={self._redirect}&state={state}&scope=email,openid,w_member_social,profile"
        
        if (not self._client_id or not self._redirect):
            print("Il manque le code !")
            return

        webbrowser.open(auth_url)
        
    def get_access_token(self) -> dict:
        if (not self._code):
            print("Vous devez obtenir un code d'accès : https://learn.microsoft.com/fr-fr/linkedin/shared/authentication/getting-access?context=linkedin%2Fcontext\
                  \nMettez ce code dans code du .env")
            self.open_url_access()
        headers: dict = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        params: dict = {
            "grant_type": "authorization_code",
            "code": self._code,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "redirect_uri": self._redirect
        }
        r = requests.post("https://www.linkedin.com/oauth/v2/accessToken", 
                          headers=headers, 
                          data=params)
        
        access_token = r.json()
        
        if (access_token.get('error')):
            print('you should retry the first step')
            self.open_url_access()
            return
        if (access_token.get('access_token')):
            print('Okay acess_token')
            self.access_token = access_token['access_token']
            self.headers["Authorization"] = f"Bearer {self.access_token}"
            self.write_token_to_env()
        else:
            print("You have an error please look at this link https://www.youtube.com/watch?v=jYflkIo1R4A&t=700s you will understand all")
        return access_token

    def get_user_urn(self) -> str:
        r = requests.get('https://api.linkedin.com/v2/userinfo', headers=self.headers)
        sub: dict = r.json()
        if (sub.get('sub')):
            print("okay got urn")
        else:
            print(sub)
            print("Regardez le message")
            self.get_access_token()
            return("")
        return sub['sub']
        
    def upload_image(self, urn: str) -> dict:
        if (not urn):
            self.get_access_token()
            return
        if (not self.image):
            print("Veuillez mettre un mot en anglais pour votre image !")
            return
        tab = {}
        os.makedirs("img", exist_ok=True)
        image_path = './img/hey.jpg'
        data = {
            "registerUploadRequest": {
                "recipes": [
                    "urn:li:digitalmediaRecipe:feedshare-image"
                ],
                "owner": "urn:li:person:"+urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        r = requests.post('https://api.linkedin.com/v2/assets?action=registerUpload', headers=self.headers, json=data)
        if (r.status_code >= 200):
            tab['src'] = r.json()['value']['asset']
            tab['url'] = r.json()['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            print(tab['url'])
            with open(image_path, mode='rb') as file:
                upload_response = requests.post(tab['url'], headers={'Authorization': 'Bearer redacted'}, data=file)
            print(upload_response)
            print('uploaded image')
            return tab
        return ""

    def create_post(self, message: str, urn: str):
        data = {
            "author": "urn:li:person:"+urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": message
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": "Image"
                            },
                            "media": self.upload_image(urn)['src'],
                            "title": {
                                "text": "Image"
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        r = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=self.headers, json=data)
        if (r.status_code == 201):
            print('created')
        print(r.json())
        
    def post(self, message: str):
        urn: str = self.get_user_urn()
        self.create_post(message, urn)
        