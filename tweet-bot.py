import os
import tweepy
import requests
import sys

# =====================
# LOAD CREDENTIALS
# =====================
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Debug: check if secrets are loaded
print("🔍 Checking environment variables...")
print("API_KEY:", "✅ Loaded" if API_KEY else "❌ Missing")
print("API_SECRET:", "✅ Loaded" if API_SECRET else "❌ Missing")
print("ACCESS_TOKEN:", "✅ Loaded" if ACCESS_TOKEN else "❌ Missing")
print("ACCESS_TOKEN_SECRET:", "✅ Loaded" if ACCESS_TOKEN_SECRET else "❌ Missing")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    print("❌ Missing one or more API credentials. Exiting.")
    sys.exit(1)

# =====================
# AUTHENTICATE
# =====================
try:
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    api.verify_credentials()
    print("✅ Authentication successful!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    sys.exit(1)

# =====================
# CONSTANTS
# =====================
HASHTAGS = "#ลูกหมีซอนญ่า #LMSY #HarmonySecret"
QUOTES_API = "https://api.quotable.io/random"

def get_random_quote():
    """Fetch a random motivational quote from Quotable API"""
    try:
        response = requests.get(QUOTES_API, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"{data['content']} — {data['author']}"
        else:
            print("⚠️ API error, using fallback quote.")
            return "Keep going, you’re doing great!"
    except:
        print("⚠️ Request failed, using fallback quote.")
        return "Dream big, work hard, and make it happen!"

def tweet_random_quote():
    """Compose and post a tweet"""
    quote = get_random_quote()
    tweet = f"{quote} {HASHTAGS}"

    # Ensure tweet <= 280 chars
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    try:
        api.update_status(tweet)
        print(f"✅ Tweet posted: {tweet}")
    except Exception as e:
        print(f"❌ Failed to post tweet: {e}")

if __name__ == "__main__":
    tweet_random_quote()
