import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_create_and_list_products():
    # Create product
    product_data = {
        "name": "Sukari 2kg",
        "description": "Sugar",
        "price": 350,
        "stock_quantity": 100,
        "is_active": True
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sukari 2kg"
    assert data["price"] == 350.0

    # List products
    response = client.get("/products/")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 1

def test_ussd_webhook_main_menu():
    # Test USSD main menu request
    response = client.post(
        "/api/ussd",
        data={
            "sessionId": "ATuid_test_123",
            "serviceCode": "*384*12039#",
            "phoneNumber": "+254712345678",
            "text": ""
        }
    )
    assert response.status_code == 200
    assert "CON Welcome to Offline Sales" in response.text

def test_ussd_webhook_browse_products():
    # Test USSD selecting option 1 (Browse Products)
    response = client.post(
        "/api/ussd",
        data={
            "sessionId": "ATuid_test_123",
            "serviceCode": "*384*12039#",
            "phoneNumber": "+254712345678",
            "text": "1"
        }
    )
    assert response.status_code == 200
    assert "Select Product" in response.text
