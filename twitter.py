import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

def tweet(message: str):
    # Replace these values with your own Twitter API credentials
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if (not consumer_key or not consumer_secret or not access_token
    or not access_token_secret or not bearer_token):
        print("Il vous manque une chose dans twitter cherchez l'api v1 et suivez toutes les étapes https://docs.x.com/x-api/getting-started/getting-access")
        return None
    
    #v1 
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    os.makedirs("img", exist_ok=True)
    image_path = './img/hey.jpg'
    media = api.media_upload(image_path)
    

    # Authenticate to Twitter
    client = tweepy.Client(bearer_token=bearer_token)

    client = tweepy.Client(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret
    )

    response = client.create_tweet(
        text=message,
        media_ids=[media.media_id]
    )
    print(f"https://twitter.com/user/status/{response.data['id']}")