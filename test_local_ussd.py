import requests

url = "http://localhost:8000/api/ussd"

# 1. We start a new session with an empty text payload
payload = {
    "sessionId": "test_session_999",
    "serviceCode": "*384*12039#",
    "phoneNumber": "+254700000000",
    "text": "" 
}

print("--- Dialing *384*12039# ---")
response = requests.post(url, data=payload)
print("Server replies:\n", response.text)

# 2. The user types "1" to browse products
payload["text"] = "1"
print("\n--- User types: 1 ---")
response = requests.post(url, data=payload)
print("Server replies:\n", response.text)

# 3. The user selects a product (e.g., "1" for Sukari)
payload["text"] = "1*1" 
print("\n--- User types: 1*1 (Select product 1) ---")
response = requests.post(url, data=payload)
print("Server replies:\n", response.text)

# 4. The user enters quantity (e.g., "2")
payload["text"] = "1*1*2" 
print("\n--- User types: 1*1*2 (Enter quantity 2) ---")
response = requests.post(url, data=payload)
print("Server replies:\n", response.text)

# 5. The user enters location (e.g., "Nairobi")
payload["text"] = "1*1*2*Nairobi" 
print("\n--- User types: 1*1*2*Nairobi (Enter location) ---")
response = requests.post(url, data=payload)
print("Server replies:\n", response.text)
