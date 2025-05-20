import requests
import os
from dotenv import load_dotenv

load_dotenv()

class Facebook:
    def __init__(self):
        self.facebook_token = os.getenv('FACEBOOK_TOKEN')
    
    def test(self):
        if not self.facebook_token:
            print("Il vous manque une token d'accès")
            return None
        
        data = {
            "access_token": self.facebook_token
        }
        
        r = requests.get(f"https://graph.facebook.com/v22.0/user_id/accounts?access_token={self.facebook_token}")
        
        print(r.request.url)
        print(r.request.body)
        print(r.json())