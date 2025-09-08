import os
import tweepy
import requests

# =====================
# CONFIGURATION
# =====================
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Authenticate with Twitter/X API
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Fixed hashtags
HASHTAGS = "#ลูกหมีซอนญ่า #LMSY #HarmonySecret"

def get_random_quote():
    """Fetch a random motivational quote from a public API"""
    try:
        response = requests.get("https://api.quotable.io/random", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"{data['content']} — {data['author']}"
        else:
            return "Stay positive and keep moving forward!"
    except Exception:
        return "Dream big and work hard every day!"

def tweet_random_quote():
    """Post a tweet with a random quote + hashtags"""
    quote = get_random_quote()
    tweet = f"{quote} {HASHTAGS}"

    # Ensure tweet stays under 280 chars
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    try:
        api.update_status(tweet)
        print(f"✅ Tweet posted: {tweet}")
    except Exception as e:
        print(f"⚠️ Error posting tweet: {e}")

if __name__ == "__main__":
    tweet_random_quote()
