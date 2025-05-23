import bot
import fetch_picture
import linkedin
import twitter
import discord
import tiktok
import facebook
import instagram
import os
from colorama import Fore, Style, init
from dotenv import load_dotenv

load_dotenv()

os.makedirs("img", exist_ok=True)

def do_all():
    if os.getenv("MESSAGE") and os.getenv("IMAGE"):
        message: str = bot.bot(os.getenv("MESSAGE"))
        fetch_picture.random()
    else:
        print("Vous devez fournir un MESSAGE et IMAGE dans le fichier .env pour générer le prompt image et message")
        return None

    if os.getenv("LINKEDIN_CLIENT_ID") and os.getenv("LINKEDIN_CLIENT_SECRET"): 
        linkedin_api = linkedin.Linkedin()
        linkedin_api.post(message)
    else:
        print('Vous devez fournir un LINKEDIN_CLIENT_ID et LINKEDIN_CLIENT_SECRET au fichier .env pour utiliser linkedin')
        print("https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow?context=linkedin%2Fcontext&tabs=HTTPS1")
        
    if (os.getenv("TWITTER_CONSUMER_KEY") and os.getenv("TWITTER_CONSUMER_SECRET")
    and os.getenv("TWITTER_ACCESS_TOKEN") and os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    and os.getenv("TWITTER_BEARER_TOKEN")):
        twitter.tweet(message)
    else:
        print('Vous devez fournir un TWITTER_CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN au fichier .env pour utiliser twiter')
        print("https://docs.x.com/x-api/getting-started/getting-access")
        
    if (os.getenv("DISCORD_ID") and os.getenv("DISCORD_CHANEL_ID") and os.getenv("DISCORD_TOKEN")):
        discord_api = discord.Discord()
        discord_api.post(message)
    else:
        print('Vous devez fournir un DISCORD_ID et DISCORD_CHANEL_ID au fichier .env pour utiliser discord')
        print("https://discord.com/developers/docs/quick-start/getting-started#step-1-creating-an-app")
        
    if (os.getenv("FACEBOOK_CLIENT_ID") and os.getenv("FACEBOOK_CLIENT_SECRET")):
        fb = facebook.Facebook()
        insta = instagram.Instagram()
        
        fb.post(message)
        insta.post_insta(message)
    else:
        print('Vous devez fournir un FACEBOOK_CLIENT_ID et FACEBOOK_CLIENT_SECRET au fichier .env pour utiliser facebook et instagram')
        print("https://developers.facebook.com/docs/facebook-login/facebook-login-for-business")

    # if os.getenv("TIKTOK_CLIENT_KEY") and os.getenv("TIKTOK_SECRET_KEY"): 
    #     tiktok_api = tiktok.Tiktok()
    #     tiktok_api.post(message)
    # else:
    #     print("Vous devez fournir un TIKTOK_CLIENT_KEY et TIKTOK_CLIENT_SECRET au fichier .env pour utiliser tiktok")
    #     print("https://developers.tiktok.com/doc/getting-started-create-an-app?enter_method=left_navigation")
    #     print("Vous devez absolment soumettre l'application sinon ça ne marchera pas")
        
do_all()

