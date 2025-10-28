from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client.tmis_business_guru

# Find the ONE client that has ie_code_number
print("=== Finding client WITH ie_code_number ===\n")
client_with_field = db.clients.find_one({'ie_code_number': {'$exists': True, '$ne': ''}})

if client_with_field:
    print(f"Client WITH ie_code_number:")
    print(f"  _id: {client_with_field.get('_id')}")
    print(f"  legal_name: {client_with_field.get('legal_name', 'N/A')}")
    print(f"  ie_code_number: {client_with_field.get('ie_code_number')}")
    print()

# Now let's manually test updating a client
print("=== Testing Manual Update ===\n")

# Find a client with IE code but no ie_code_number
test_client = db.clients.find_one({'ie_code': {'$exists': True, '$ne': ''}, 'ie_code_number': {'$exists': False}})

if test_client:
    test_id = test_client['_id']
    print(f"Test client: {test_id}")
    print(f"  Before: ie_code_number = {test_client.get('ie_code_number', 'NOT_PRESENT')}")
    
    # Try to update it
    result = db.clients.update_one(
        {'_id': test_id},
        {'$set': {'ie_code_number': 'TEST123456'}}
    )
    
    print(f"  Update result: matched={result.matched_count}, modified={result.modified_count}")
    
    # Check if it was saved
    updated_client = db.clients.find_one({'_id': test_id})
    print(f"  After: ie_code_number = {updated_client.get('ie_code_number', 'NOT_PRESENT')}")
    
    if updated_client.get('ie_code_number') == 'TEST123456':
        print("  ✅ Manual update SUCCESSFUL!")
    else:
        print("  ❌ Manual update FAILED!")
else:
    print("No test client found")
