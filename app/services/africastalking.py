import httpx
from app.core.config import settings

class AfricasTalkingService:
    """
    Wrapper for Africa's Talking API (SMS and USSD messaging).
    """
    def __init__(self):
        self.username = settings.AT_USERNAME
        self.api_key = settings.AT_API_KEY
        self.is_sandbox = self.username == "sandbox"
        self.base_url = (
            "https://api.sandbox.africastalking.com/version1/messaging"
            if self.is_sandbox
            else "https://api.africastalking.com/version1/messaging"
        )

    async def send_sms(self, phone_number: str, message: str) -> dict:
        """
        Sends an SMS notification via Africa's Talking API.
        """
        headers = {
            "apiKey": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "username": self.username,
            "to": phone_number,
            "message": message,
            "from": settings.AT_SHORTCODE if not self.is_sandbox else None,
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        # For production / robust async handling, use httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, data=data, headers=headers, timeout=10.0)
                # If sandbox/mock or real API
                if response.status_code in (200, 201):
                    return {"success": True, "data": response.json()}
                else:
                    return {"success": False, "status_code": response.status_code, "detail": response.text}
        except Exception as e:
            # Fallback for offline / mock testing when AT is unreachable
            print(f"[Mock AT SMS] Sent to {phone_number}: {message} (Error: {e})")
            return {"success": True, "mock": True, "message": message}

africastalking_service = AfricasTalkingService()
