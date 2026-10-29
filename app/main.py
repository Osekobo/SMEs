from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.api import products, ussd, webhooks, mpesa
from app.db.session import AsyncSessionLocal, get_db
from app.models.product import Product

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
async def startup_event():
    """
    Automatically seed shoe products on startup if none exist.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product).where(
                Product.name.ilike("%shoe%") | 
                Product.name.ilike("%sneaker%") | 
                Product.name.ilike("%nike%")
            )
        )
        existing = result.scalars().all()
        if not existing:
            shoe1 = Product(
                name="Nike Air Force Sneaker",
                description="Stylish comfort sneakers",
                price=3500.0,
                stock_quantity=25,
                is_active=True
            )
            shoe2 = Product(
                name="Nike Air Max Runner",
                description="High performance running sneakers",
                price=4200.0,
                stock_quantity=15,
                is_active=True
            )
            session.add_all([shoe1, shoe2])
            await session.commit()

# Include routers
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
async def demo_status(db: AsyncSession = Depends(get_db)):
    # Fetch active shoe/product items from database
    result = await db.execute(select(Product).where(Product.is_active == True).limit(2))
    db_products = result.scalars().all()
    
    # Fallback if no products in DB
    if not db_products:
        class Fallback:
            name = "Nike Air Force Sneaker"
            price = 3500.0
        db_products = [Fallback(), Fallback()]

    img1 = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=400&q=80"
    img2 = "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=400&q=80"
    
    p1_name = db_products[0].name
    p1_price = int(db_products[0].price) if float(db_products[0].price).is_integer() else db_products[0].price
    
    p2_name = db_products[1].name if len(db_products) > 1 else p1_name
    p2_price = int(db_products[1].price) if len(db_products) > 1 and float(db_products[1].price).is_integer() else (db_products[1].price if len(db_products) > 1 else p1_price)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WhatsApp Status Demo</title>
        <style>
            body {{ margin: 0; padding: 0; font-family: sans-serif; background-color: #000; display: flex; justify-content: center; align-items: center; height: 100vh; color: white; user-select: none; }}
            .phone {{ width: 100%; max-width: 400px; height: 100vh; max-height: 800px; background-color: #111b21; position: relative; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 0 20px rgba(0,0,0,0.8); }}
            
            /* Status Progress Bars */
            .progress-container {{ display: flex; gap: 4px; padding: 10px 15px; z-index: 20; background: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent); }}
            .progress-bar {{ flex: 1; height: 3px; background-color: rgba(255,255,255,0.4); border-radius: 2px; overflow: hidden; position: relative; }}
            .progress-fill {{ width: 0%; height: 100%; background-color: #fff; transition: width linear; }}
            .progress-fill.active {{ width: 100%; transition-duration: 5s; }}
            .progress-fill.completed {{ width: 100%; transition-duration: 0s; }}

            .header {{ padding: 5px 15px 15px 15px; display: flex; align-items: center; z-index: 10; background: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent); }}
            .back-arrow {{ font-size: 24px; margin-right: 15px; cursor: pointer; }}
            .profile {{ display: flex; align-items: center; }}
            .avatar {{ width: 40px; height: 40px; border-radius: 50%; background-color: #25D366; display: flex; justify-content: center; align-items: center; font-weight: bold; margin-right: 10px; }}
            .name {{ font-weight: bold; font-size: 16px; }}
            .time {{ font-size: 12px; color: #ccc; }}
            
            /* Slides */
            .slides-wrapper {{ flex: 1; position: relative; overflow: hidden; display: flex; }}
            .slide {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: none; flex-direction: column; justify-content: center; align-items: center; padding: 20px; text-align: center; box-sizing: border-box; }}
            .slide.active {{ display: flex; }}
            
            .slide-1 {{ background: linear-gradient(45deg, #1e3c72, #2a5298); }}
            .slide-2 {{ background: linear-gradient(45deg, #3a1c71, #d76d77, #ffaf7b); }}

            .product-image {{ width: 80%; max-height: 350px; object-fit: cover; border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); margin-bottom: 20px; }}
            .story-text {{ font-size: 22px; font-weight: bold; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }}
            .story-price {{ font-size: 20px; color: #ffd700; margin-bottom: 20px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }}

            /* Tap Navigation Zones */
            .tap-left {{ position: absolute; top: 0; left: 0; width: 30%; height: 100%; z-index: 15; cursor: pointer; }}
            .tap-right {{ position: absolute; top: 0; right: 0; width: 70%; height: 100%; z-index: 15; cursor: pointer; }}

            .footer {{ padding: 20px; z-index: 20; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); text-align: center; }}
            .swipe-link {{ background-color: #25D366; color: white; padding: 12px 20px; border-radius: 30px; text-decoration: none; font-size: 16px; font-weight: bold; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.4); border: none; cursor: pointer; width: 90%; }}
            .copy-link {{ background-color: transparent; color: #ccc; border: 1px solid #ccc; padding: 8px; border-radius: 5px; margin-top: 10px; cursor: pointer; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="phone">
            <!-- Progress Bars -->
            <div class="progress-container">
                <div class="progress-bar"><div class="progress-fill" id="p-0"></div></div>
                <div class="progress-bar"><div class="progress-fill" id="p-1"></div></div>
            </div>

            <div class="header">
                <div class="back-arrow">&#8592;</div>
                <div class="profile">
                    <div class="avatar">S</div>
                    <div>
                        <div class="name">Sneaker Store KE</div>
                        <div class="time" id="status-time">Just now</div>
                    </div>
                </div>
            </div>
            
            <!-- Slides Container -->
            <div class="slides-wrapper">
                <div class="tap-left" onclick="prevSlide()"></div>
                <div class="tap-right" onclick="nextSlide()"></div>

                <!-- Slide 1 (Dynamic Product 1) -->
                <div class="slide slide-1 active" id="slide-0">
                    <img src="{img1}" alt="{p1_name}" class="product-image">
                    <div class="story-text">{p1_name}</div>
                    <div class="story-price">Only KES {p1_price:,}!</div>
                </div>

                <!-- Slide 2 (Dynamic Product 2) -->
                <div class="slide slide-2" id="slide-1">
                    <img src="{img2}" alt="{p2_name}" class="product-image">
                    <div class="story-text">{p2_name}</div>
                    <div class="story-price">Only KES {p2_price:,}!</div>
                </div>
            </div>
            
            <div class="footer">
                <a href="tel:*384*12039%23" class="swipe-link">
                    📞 Tap to Dial *384*12039#
                </a>
                <br>
                <button onclick="copyCode()" class="copy-link" id="copyBtn">App blocked dialing? Tap to Copy Code</button>
            </div>
        </div>

        <script>
            let currentSlide = 0;
            const totalSlides = 2;
            const slideDuration = 5000;
            let timer;

            function showSlide(index) {{
                clearTimeout(timer);
                if (index >= totalSlides) {{
                    currentSlide = 0;
                }} else if (index < 0) {{
                    currentSlide = totalSlides - 1;
                }} else {{
                    currentSlide = index;
                }}

                document.querySelectorAll('.slide').forEach((slide, i) => {{
                    slide.classList.toggle('active', i === currentSlide);
                }});

                document.querySelectorAll('.progress-fill').forEach((bar, i) => {{
                    bar.classList.remove('active', 'completed');
                    if (i < currentSlide) {{
                        bar.classList.add('completed');
                    }} else if (i === currentSlide) {{
                        void bar.offsetWidth;
                        bar.classList.add('active');
                    }}
                }});

                timer = setTimeout(() => {{
                    showSlide(currentSlide + 1);
                }}, slideDuration);
            }}

            function nextSlide() {{
                showSlide(currentSlide + 1);
            }}

            function prevSlide() {{
                showSlide(currentSlide - 1);
            }}

            function copyCode() {{
                navigator.clipboard.writeText("*384*12039#").then(function() {{
                    var btn = document.getElementById("copyBtn");
                    btn.innerText = "✅ Copied! Open dialer & paste.";
                    btn.style.color = "#25D366";
                    btn.style.borderColor = "#25D366";
                }});
            }}

            showSlide(0);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
