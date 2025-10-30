from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client.tmis_business_guru

# Find a client with IE code showing "9999999999"
print("=== Searching for clients with IE code ===\n")

# Find all clients with IE code
clients = db.clients.find({'ie_code': {'$exists': True, '$ne': ''}}).limit(5)

for idx, sample in enumerate(clients, 1):
    print(f"Client {idx}:")
    print(f"  _id: {sample.get('_id')}")
    print(f"  legal_name: {sample.get('legal_name', 'N/A')}")
    print(f"  ie_code: {sample.get('ie_code', 'NOT_FOUND')}")
    print(f"  ie_code_number: {sample.get('ie_code_number', 'NOT_FOUND')}")
    print(f"  All keys containing 'ie':")
    for key in sample.keys():
        if 'ie' in key.lower():
            print(f"    {key}: {sample.get(key)}")
    print()

# Also check if any client has ie_code_number field at all
count_with_ie_code_number = db.clients.count_documents({'ie_code_number': {'$exists': True, '$ne': ''}})
print(f"\nTotal clients with ie_code_number field: {count_with_ie_code_number}")
