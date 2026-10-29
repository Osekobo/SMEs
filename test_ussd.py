import httpx

def test_ussd():
    url = "http://localhost:8000/api/ussd"
    data = {
        "sessionId": "ATuid_12345",
        "serviceCode": "*384*12039#",
        "phoneNumber": "+254712345678",
        "text": ""
    }
    response = httpx.post(url, data=data)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

if __name__ == "__main__":
    test_ussd()
