from diffusers import StableDiffusionPipeline
import torch
import os
from dotenv import load_dotenv

load_dotenv()

def image(msg: str = "poule", path: str = "img/hey.jpg"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5", 
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )
    pipe = pipe.to(device)

    prompt = os.getenv('MESSAGE') if os.getenv('MESSAGE') else msg 
    image = pipe(prompt).images[0]
    os.makedirs("img", exist_ok=True)
    image.save("img/hey.jpg")
    print("image saved !")