from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.product import Product
from app.models.order import Order
from app.services.mpesa import mpesa_service
from app.services.africastalking import africastalking_service

router = APIRouter(prefix="", tags=["SMS"])

@router.post("/api/sms/inbound")
async def inbound_sms(
    from_: str = Form(..., alias="from"),
    text: str = Form(...),
    date: str | None = Form(None),
    id: str | None = Form(None),
    linkId: str | None = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Africa's Talking Inbound SMS Webhook.
    If text is "1", creates an Order for the featured product, triggers M-Pesa STK push, and replies via SMS.
    """
    cleaned_text = text.strip().lower()
    
    if cleaned_text == "1":
        # Fetch first active product as default featured product
        prod_result = await db.execute(select(Product).where(Product.is_active == True).limit(1))
        product = prod_result.scalars().first()
        
        if not product:
            await africastalking_service.send_sms(
                phone_number=from_,
                message="Sorry, no products are currently available for purchase."
            )
            return Response(content="<Response></Response>", media_type="application/xml")
        
        quantity = 1
        total_amount = float(product.price) * quantity
        
        # Create Order in PENDING_PAYMENT status
        order = Order(
            phone_number=from_,
            product_id=product.id,
            quantity=quantity,
            total_amount=total_amount,
            delivery_location="Standard Delivery (SMS)",
            status="PENDING_PAYMENT"
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        # Trigger M-Pesa STK Push
        await mpesa_service.initiate_stk_push(
            phone_number=from_,
            amount=total_amount,
            account_reference=f"Order #{order.id}"
        )
        
        # Reply via outbound SMS
        await africastalking_service.send_sms(
            phone_number=from_,
            message=f"Order #{order.id} for {product.name} (KES {total_amount}) created! Enter your M-Pesa PIN on your phone to complete payment."
        )
    else:
        await africastalking_service.send_sms(
            phone_number=from_,
            message="Thank you for your message. Reply '1' to order our featured product instantly."
        )

    # Africa's Talking expects XML or plain text response for SMS callbacks
    return Response(content="<Response></Response>", media_type="application/xml")
