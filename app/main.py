from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.api import products, ussd, webhooks, mpesa

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers (SMS removed)
app.include_router(products.router)
app.include_router(ussd.router)
app.include_router(webhooks.router)
app.include_router(mpesa.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Offline Sales Automation System (USSD & M-Pesa Backend)",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/shop", response_class=HTMLResponse)
async def shop_bridge():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Shop with us!</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f9; padding: 20px; color: #333; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); max-width: 400px; margin: 0 auto; }
            h1 { color: #0056b3; }
            .btn { display: block; background-color: #28a745; color: white; padding: 15px; text-decoration: none; border-radius: 5px; font-size: 20px; font-weight: bold; margin: 20px 0; cursor: pointer; border: none; width: 100%; }
            .btn:active { background-color: #218838; }
            .copy-btn { background-color: #007bff; font-size: 16px; padding: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Order Offline</h1>
            <p>No internet needed! Click the button below to open your phone dialer and shop.</p>
            
            <a href="tel:*384*12039%23" class="btn">📞 Dial *384*12039#</a>
            
            <p style="font-size: 14px; color: #666;">If the button doesn't work on your phone, copy the code below and dial it manually:</p>
            
            <button onclick="copyCode()" class="btn copy-btn" id="copyBtn">Copy *384*12039#</button>
        </div>

        <script>
            function copyCode() {
                navigator.clipboard.writeText("*384*12039#").then(function() {
                    var btn = document.getElementById("copyBtn");
                    btn.innerText = "✅ Copied! Now paste in your dialer.";
                    btn.style.backgroundColor = "#28a745";
                });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/demo-status", response_class=HTMLResponse)
async def demo_status():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WhatsApp Status Demo</title>
        <style>
            body { margin: 0; padding: 0; font-family: sans-serif; background-color: #000; display: flex; justify-content: center; align-items: center; height: 100vh; color: white; }
            .phone { width: 100%; max-width: 400px; height: 100vh; max-height: 800px; background-color: #111b21; position: relative; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
            .header { padding: 15px; display: flex; align-items: center; z-index: 10; background: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent); }
            .back-arrow { font-size: 24px; margin-right: 15px; cursor: pointer; }
            .profile { display: flex; align-items: center; }
            .avatar { width: 40px; height: 40px; border-radius: 50%; background-color: #25D366; display: flex; justify-content: center; align-items: center; font-weight: bold; margin-right: 10px; }
            .name { font-weight: bold; font-size: 16px; }
            .time { font-size: 12px; color: #ccc; }
            .story-content { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px; text-align: center; background: linear-gradient(45deg, #1e3c72, #2a5298); }
            .product-image { width: 80%; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); margin-bottom: 20px; }
            .story-text { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
            .story-price { font-size: 20px; color: #ffd700; margin-bottom: 20px; }
            .footer { padding: 20px; z-index: 10; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); text-align: center; }
            
            /* Styling for the direct dial link */
            .swipe-link { background-color: #25D366; color: white; padding: 15px 30px; border-radius: 30px; text-decoration: none; font-size: 18px; font-weight: bold; display: inline-block; animation: bounce 1.5s infinite; border: none; cursor: pointer; width: 80%; }
            .copy-link { background-color: transparent; color: #ccc; border: 1px solid #ccc; padding: 10px; border-radius: 5px; margin-top: 15px; cursor: pointer; font-size: 14px; }
            
            @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        </style>
    </head>
    <body>
        <div class="phone">
            <div class="header">
                <div class="back-arrow">&#8592;</div>
                <div class="profile">
                    <div class="avatar">S</div>
                    <div>
                        <div class="name">Sukari Store</div>
                        <div class="time">Just now</div>
                    </div>
                </div>
            </div>
            
            <div class="story-content">
                <img src="https://images.unsplash.com/photo-1581441363689-1f3c3c414635?auto=format&fit=crop&w=400&q=80" alt="Sugar" class="product-image">
                <div class="story-text">Sukari 2kg</div>
                <div class="story-price">Only KES 350!</div>
            </div>
            
            <div class="footer">
                <!-- This is the direct dial link -->
                <a href="tel:*384*12039%23" class="swipe-link">
                    📞 Tap to Dial *384*12039#
                </a>
                
                <!-- Fallback if the app blocks the dialer -->
                <br>
                <button onclick="copyCode()" class="copy-link" id="copyBtn">App blocked dialing? Tap to Copy Code</button>
            </div>
        </div>

        <script>
            function copyCode() {
                navigator.clipboard.writeText("*384*12039#").then(function() {
                    var btn = document.getElementById("copyBtn");
                    btn.innerText = "✅ Copied! Open your dialer and paste.";
                    btn.style.color = "#25D366";
                    btn.style.borderColor = "#25D366";
                });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
