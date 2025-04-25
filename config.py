from dotenv import load_dotenv
import os

load_dotenv()

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_PARTNER_TAG = os.getenv("AMAZON_PARTNER_TAG")
AMAZON_MARKETPLACE = os.getenv("DEFAULT_MARKETPLACE", "www.amazon.com")
AMAZON_REGION = os.getenv("DEFAULT_REGION", "us-east-1")
CACHE_DURATION_HOURS = 12
USE_DUMMY_DATA = os.getenv("USE_DUMMY_DATA", "False") == "True"
