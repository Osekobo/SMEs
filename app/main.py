from fastapi import FastAPI
from app.core.config import settings
from app.api import products, ussd, sms, webhooks, mpesa

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(products.router)
app.include_router(ussd.router)
app.include_router(sms.router)
app.include_router(webhooks.router)
app.include_router(mpesa.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Offline Sales Automation System (USSD & M-Pesa Backend)",
        "docs": "/docs",
        "status": "online"
    }
