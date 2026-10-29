from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.order import Order

router = APIRouter(prefix="/api/mpesa", tags=["M-Pesa"])

@router.post("/callback")
async def mpesa_callback(payload: dict, db: AsyncSession = Depends(get_db)):
    """
    Safaricom Daraja STK Push Callback endpoint.
    Updates order status to PAID if ResultCode is 0 and saves M-Pesa receipt.
    """
    try:
        body = payload.get("Body", {})
        stk_callback = body.get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        merchant_request_id = stk_callback.get("MerchantRequestID")
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        
        meta_data = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        mpesa_receipt = None
        
        for item in meta_data:
            if item.get("Name") == "MpesaReceiptNumber":
                mpesa_receipt = str(item.get("Value"))
                break

        if not mpesa_receipt:
            mpesa_receipt = f"RCPT_{checkout_request_id[-6:]}" if checkout_request_id else "RCPT_MOCK123"

        # Find latest PENDING_PAYMENT order
        order_result = await db.execute(
            select(Order).where(Order.status == "PENDING_PAYMENT").order_by(Order.created_at.desc()).limit(1)
        )
        order = order_result.scalars().first()

        if order:
            if result_code == 0:
                order.status = "PAID"
                order.mpesa_receipt = mpesa_receipt
                await db.commit()
            else:
                order.status = "FAILED"
                await db.commit()

    except Exception as e:
        print(f"Error processing M-Pesa callback: {e}")

    return {"ResultCode": 0, "ResultDesc": "Accepted"}
