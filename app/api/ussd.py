from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.ussd_session import USSDSession
from app.models.product import Product
from app.models.order import Order
from app.services.mpesa import mpesa_service

router = APIRouter(prefix="", tags=["USSD"])

@router.post("/api/ussd")
async def ussd_webhook(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(default=""),
    db: AsyncSession = Depends(get_db)
):
    """
    Africa's Talking USSD Webhook endpoint.
    Maintains session state in database and parses cumulative text payload.
    """
    # Retrieve or create USSD session
    result = await db.execute(select(USSDSession).where(USSDSession.session_id == sessionId))
    session = result.scalars().first()
    
    if not session:
        session = USSDSession(
            session_id=sessionId,
            phone_number=phoneNumber,
            current_state="MAIN_MENU",
            cart_data={}
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # Parse text parts
    text_parts = text.split("*") if text else []
    response_text = ""

    # Root / Main Menu (empty text or just "" )
    if not text or text == "":
        session.current_state = "MAIN_MENU"
        session.cart_data = {}
        await db.commit()
        
        response_text = "CON Welcome to Offline Sales\n1. Browse Products\n2. Check Order Status"
        return Response(content=response_text, media_type="text/plain")

    # If user selected option 1: Browse Products
    if text_parts[0] == "1":
        if len(text_parts) == 1:
            # Fetch active products from DB
            prod_result = await db.execute(select(Product).where(Product.is_active == True))
            products = prod_result.scalars().all()
            
            if not products:
                return Response(content="END No products available at the moment.", media_type="text/plain")
            
            menu = "CON Select Product:\n"
            for idx, p in enumerate(products, start=1):
                menu += f"{idx}. {p.name} - KES {p.price}\n"
            return Response(content=menu, media_type="text/plain")

        # User selected a product index (e.g., "1*1")
        elif len(text_parts) == 2:
            prod_idx = int(text_parts[1]) - 1
            prod_result = await db.execute(select(Product).where(Product.is_active == True))
            products = prod_result.scalars().all()
            
            if prod_idx < 0 or prod_idx >= len(products):
                return Response(content="END Invalid product selection.", media_type="text/plain")
            
            selected_product = products[prod_idx]
            session.cart_data = {"product_id": selected_product.id, "product_name": selected_product.name, "price": float(selected_product.price)}
            session.current_state = "AWAITING_QUANTITY"
            await db.commit()
            
            return Response(content=f"CON Enter quantity for {selected_product.name}:", media_type="text/plain")

        # User entered quantity (e.g., "1*1*2")
        elif len(text_parts) == 3:
            try:
                quantity = int(text_parts[2])
                if quantity <= 0:
                    raise ValueError()
            except ValueError:
                return Response(content="END Invalid quantity entered.", media_type="text/plain")
            
            cart = session.cart_data or {}
            cart["quantity"] = quantity
            session.cart_data = cart
            session.current_state = "AWAITING_LOCATION"
            await db.commit()
            
            return Response(content="CON Enter delivery location (e.g., Nairobi, CBD):", media_type="text/plain")

        # User entered delivery location (e.g., "1*1*2*CBD") -> Finalize Order & Trigger STK Push
        elif len(text_parts) == 4:
            location = text_parts[3]
            cart = session.cart_data or {}
            product_id = cart.get("product_id")
            quantity = cart.get("quantity", 1)
            price = cart.get("price", 0.0)
            
            if not product_id:
                return Response(content="END Session error. Please restart.", media_type="text/plain")
            
            total_amount = price * quantity
            
            # Create Order in DB
            order = Order(
                phone_number=phoneNumber,
                product_id=product_id,
                quantity=quantity,
                total_amount=total_amount,
                delivery_location=location,
                status="PENDING_PAYMENT"
            )
            db.add(order)
            await db.commit()
            await db.refresh(order)
            
            # Trigger M-Pesa STK Push
            stk_res = await mpesa_service.initiate_stk_push(
                phone_number=phoneNumber,
                amount=total_amount,
                account_reference=f"Order #{order.id}"
            )
            
            return Response(
                content=f"END Order #{order.id} placed successfully! Total: KES {total_amount}. Check your phone for M-Pesa checkout.",
                media_type="text/plain"
            )

    # If user selected option 2: Check Order Status
    elif text_parts[0] == "2":
        # Fetch latest order for this phone number
        order_result = await db.execute(
            select(Order).where(Order.phone_number == phoneNumber).order_by(Order.created_at.desc()).limit(1)
        )
        latest_order = order_result.scalars().first()
        
        if not latest_order:
            return Response(content="END You have no recent orders.", media_type="text/plain")
        
        status_msg = (
            f"END Latest Order #{latest_order.id}\n"
            f"Amount: KES {latest_order.total_amount}\n"
            f"Status: {latest_order.status}\n"
            f"Location: {latest_order.delivery_location}"
        )
        return Response(content=status_msg, media_type="text/plain")

    return Response(content="END Invalid option selected.", media_type="text/plain")
