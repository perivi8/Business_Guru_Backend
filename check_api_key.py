from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv('BREVO_API_KEY')
if key:
    print(f"API Key format: {key[:20]}... (length: {len(key)})")
    print(f"Starts with 'xsmtpsib-': {key.startswith('xsmtpsib-')}")
else:
    print("API Key not found")
