import os
import random
import tweepy

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

# Example quotes (add as many as you want)
quotes = [
    "Believe in yourself and all that you are.",
    "Success is not for the lazy — keep moving forward!",
    "Dream big, work hard, stay consistent.",
    "Every day is a new opportunity to grow.",
    "Stay positive, work hard, and make it happen.",
    "Happiness is not by chance, but by choice."
]

# Fixed hashtags
HASHTAGS = "#ลูกหมีซอนญ่า #LMSY #HarmonySecret"

def tweet_random_quote():
    # Pick a random quote and append hashtags
    quote = random.choice(quotes)
    tweet = f"{quote} {HASHTAGS}"

    # Ensure tweet is under 280 characters
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    try:
        api.update_status(tweet)
        print(f"✅ Tweet posted: {tweet}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    tweet_random_quote()
