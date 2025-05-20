import os
from dotenv import load_dotenv
import requests
import random
import string
import webbrowser
from moviepy import ImageClip
import math

load_dotenv()

class Tiktok:
    def __init__(self):
        self.client_key = os.getenv('TIKTOK_CLIENT_KEY')
        self.client_secret = os.getenv('TIKTOK_SECRET_KEY')
        self.redirect_uri = os.getenv('CODE_URI')
        self.code = os.getenv('TIKTOK_CODE')
        self.access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
        self.refresh_token = os.getenv('TIKTOK_REFRESH_TOKEN')
        self.API_URL = 'https://open.tiktokapis.com/v2'
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
    # Ne marche pas sur firefox je ne sais pas pourquoi 
    def get_auth_url(self):
        if not self.client_key:
            print("Vous devez mettre une client key")
            return
        """Generate authorization URL for TikTok login"""
        state = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        scope = 'user.info.basic,video.publish,video.upload'
        
        auth_url = (
            f"https://www.tiktok.com/v2/auth/authorize/?"
            f"client_key={self.client_key}&"
            f"scope={scope}&"
            f"response_type=code&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}"
        )
        
        print(auth_url)
        
        webbrowser.open(auth_url)
        print("Please login and authorize the app. The code will be in the redirect URL with chrome.")
        
    def get_access_token(self):
        if not self.code:
            self.get_auth_url()
            print("No authorization code found. Please run get_auth_url() first.")
            return None
            
        url: str = f"{self.API_URL}/oauth/token/"
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "code": self.code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        response = requests.post(url, data=data, headers=self.headers)
        
        if response.status_code == 200:
            token_data = response.json()
            print(token_data)
            if (token_data.get("error")):
                self.get_auth_url()
                return None
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            
            # Save tokens to .env
            self.write_token_to_env('TIKTOK_ACCESS_TOKEN', self.access_token)
            self.write_token_to_env('TIKTOK_REFRESH_TOKEN', self.refresh_token)
            return token_data
        else:
            print(f"Error getting access token: {response.text}")
            return None
        
    def get_refresh_token(self):
        if not self.code:
            self.get_auth_url()
            print("No authorization code found. Please run get_auth_url() first.")
            return None
            
        url: str = f"{self.API_URL}/oauth/token/"
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        response = requests.post(url, data=data, headers=self.headers)
        
        if response.status_code == 200:
            token_data = response.json()
            print(token_data)
            if (token_data.get("error")):
                self.get_access_token()
                return None
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            
            # Save tokens to .env
            self.write_token_to_env('TIKTOK_ACCESS_TOKEN', self.access_token)
            self.write_token_to_env('TIKTOK_REFRESH_TOKEN', self.refresh_token)
            return token_data
        else:
            print(f"Error getting access token: {response.text}")
            return None
            
    def write_token_to_env(self, token_name, token_value):
        """Write token to .env file"""
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'r') as file:
            lines = file.readlines()
        
        token_line = f"{token_name}={token_value}\n"
        token_found = False
        
        for i, line in enumerate(lines):
            if line.startswith(f'{token_name}='):
                lines[i] = token_line
                token_found = True
                break
                
        if not token_found:
            lines.append(token_line)
            
        with open(env_path, 'w') as file:
            file.writelines(lines)
       
    def convert_image_to_video(self, image_path: str, duration: int = 5) -> str:
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.path.dirname(__file__), 'videos')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output video path
            video_path = os.path.join(output_dir, 'output.mp4')
            
            # Create video clip from image
            image_clip = ImageClip(image_path, duration=duration)
            
            # Write video file
            image_clip.write_videofile(
                video_path,
                fps=24,
                codec='libx264',
                audio=False
            )
            
            # Clean up
            image_clip.close()
            
            return video_path
            
        except Exception as e:
            print(f"Error converting image to video: {str(e)}")
            return None     
    
    
    def post(self, description: str, photo_path: str = "./img/hey.jpg"):
        """Upload and publish a photo to TikTok"""
        if not self.access_token:
            print("No access token found. Please authenticate first.")
            return None
        self.get_refresh_token()
        
        # Convert image to video
        video_path = self.convert_image_to_video(photo_path)
        if not video_path:
            print("La conversion a échoué !")
            return None
            
        # Step 1: Initialize content upload
        init_url = f"{self.API_URL}/post/publish/video/init/"
        self.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        })
        
        # Get video file size
        video_size = os.path.getsize(video_path)
        
        # Calculate total chunks needed
        total_chunk_count = math.floor(video_size / video_size)
        
        init_data = {
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size":  video_size,
                "total_chunk_count": total_chunk_count
            }
        }
        
        init_response = requests.post(init_url, headers=self.headers, json=init_data)
        
        if init_response.status_code != 200:
            print(f"Error initializing upload: {init_response.text}")
            return None
            
        init_data = init_response.json()
        publish_id = init_data.get('data', {}).get('publish_id')
        upload_url = init_data.get('data', {}).get('upload_url')
        
        if not publish_id or not upload_url:
            print("Missing publish_id or upload_url in response")
            return None