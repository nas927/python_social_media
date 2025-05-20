import requests
import urllib.request
import psutil
import image
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

def compress_image(input_path: str, quality: int = 60) -> str:
    # Get the directory and filename
    dir_path = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    
    print(f"Taille originale: {os.path.getsize(input_path) / 1024:.2f} KB")
    
    # Create output filename
    output_path = os.path.join(dir_path, f"{name}{ext}")
    
    # Open image
    img = Image.open(input_path)
    
    # Convert to RGB if necessary
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Save with compression
    img.save(
        output_path,
        optimize=True,
        quality=quality
    )
    
    print(f"Image compressée sauvegardée : {output_path}")
    print(f"Taille compressée: {os.path.getsize(output_path) / 1024:.2f} KB")
    
    return output_path

def download_image(url, save_as):
    urllib.request.urlretrieve(url, save_as)

def random(query="laptop"):
    client_id: str = os.getenv('UNSPLASH_CLIENT_ID')
    if not client_id:
        print("Veuillez définir un client id pour unsplash")
        return None
    memory =  psutil.virtual_memory()
    total: int = memory.total / (1024 ** 3)
    print(f"Mémoire totale : {total:.2f} Go")
    print(f"% Mémoire utilisé : {memory.percent} %")
    
    os.makedirs("img", exist_ok=True)
    save_as = './img/hey.jpg'

    if (total < 64):
        API_URL = "https://api.unsplash.com/photos/random/?client_id=tVobtEo0P6rmXCWfYkSZC4SYF_StTRb5GAbJdrDA1Go&query="+query

        response = requests.get(
            API_URL,
        )

        if (response.status_code >= 200):
            url = response.json()['urls']['raw']
            download_image(url, save_as)
            print('image saved !')
    else:
        image.image()
        
    compress_image(save_as)