


# import requests

# def get_banks():
#     url = "https://api.paystack.co/bank"
#     headers = {
#         "Authorization": "Bearer sk_test_449b06a291136c5a7b507d7c1aa8362b93e7fb5a"
#     }

#     response = requests.get(url, headers=headers)
    
#     if response.status_code == 200:
#         banks = response.json().get('data', [])
#         simplified_banks = [
#             {'name': bank['name'], 'code': bank['code']} 
#             for bank in banks
#         ]
#         return simplified_banks
#     else:
#         print("Error fetching banks:", response.json())
#         return []

# # Example usage
# banks_list = get_banks()
# print(banks_list)



import requests
import uuid

# Mock Paystack settings
PAYSTACK_BASE_URL = "https://api.paystack.co"
PAYSTACK_SECRET_KEY = "sk_test_449b06a291136c5a7b507d7c1aa8362b93e7fb5a"

def initiate_bulk_transfer(transfers):
    """Initiates bulk transfer to multiple recipients."""
    
    url = f"{PAYSTACK_BASE_URL}/transfer/bulk"
    headers = {
        'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
    }
    
    # Payload for the bulk transfer
    payload = {
        "source": "balance",
         "currency": "NGN",
        "transfers": transfers,
    }

    # Debugging - print the payload being sent
    print(f"Initiating transfer with payload: {payload}")
    
    # Actual request to Paystack API
    response = requests.post(url, json=payload, headers=headers)
    
    # Print and return the response for debugging
    print(f"Paystack response: {response.json()}")
    return response.json()

def prepare_transfer(amount, recipient_code):
    """Prepares a single transfer with unique reference."""
    
    # Ensure amount is in kobo and convert it to an integer
    amount_in_kobo = int(amount) * 100
    
    # Debugging - print the converted amount
    print(f"Converted amount (kobo): {amount_in_kobo}")

    # Generate a unique reference for each transaction
    unique_reference = f"ref_{str(uuid.uuid4())[:8]}"

    # Prepare individual transfer payload
    transfer = {
        "amount": amount_in_kobo,
        "recipient": recipient_code,
        "reference": unique_reference,
    }
    
    return transfer

def process_bulk_transfers(transactions):
    """Processes a list of transactions for bulk transfers."""
    
    # Prepare the list of transfers
    transfers = []

    for transaction in transactions:
        # Get the transaction details
        amount = transaction['amount']
        recipient = transaction['recipient']
        
        # Debugging - print the amount and recipient to ensure correctness
        print(f"Preparing transfer for amount: {amount} to recipient: {recipient}")
        
        # Prepare the transfer object
        transfer = prepare_transfer(amount, recipient)
        transfers.append(transfer)
    
    # Initiate the bulk transfer
    print(f"Initiating bulk transfer with payload: {transfers}")
    
    # Call Paystack API (mocked)
    response = initiate_bulk_transfer(transfers)
    
    # Handle and print the response
    if not response.get('status'):
        print(f"Bulk transfer failed: {response.get('message')}")
        print(f"Full response: {response}")
    else:
        print(f"Bulk transfer successful: {response.get('message')}")
        print(f"Full response: {response}")
    
    return response

# Example Transaction List for Testing
transactions = [
    {"amount": 7000, "recipient": "RCP_90a57dazj3br622"},
    {"amount": 5000, "recipient": "RCP_90a57dazj3br622"},
    {"amount": 12000, "recipient": "RCP_90a57dazj3br622"},
]

# Test the bulk transfer process with mock data
print("=== Testing Bulk Transfer Logic ===")
process_bulk_transfers(transactions)
