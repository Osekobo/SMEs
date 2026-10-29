from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.lead import Lead
from app.models.product import Product
from app.schemas.lead import MetaLeadRequest, LeadResponse
from app.services.africastalking import africastalking_service

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

@router.post("/meta-leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def meta_leads_webhook(lead_in: MetaLeadRequest, db: AsyncSession = Depends(get_db)):
    """
    Accepts Meta (Facebook/Instagram) Lead Ads webhook payload,
    creates a Lead record, and triggers an automated outbound SMS via Africa's Talking.
    """
    # 1. Create Lead record
    lead = Lead(
        name=lead_in.name,
        phone_number=lead_in.phone_number,
        source=lead_in.source,
        product_interest=lead_in.product_interest,
        status="NEW"
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    # 2. Find matching product or default price
    prod_result = await db.execute(
        select(Product).where(Product.name.ilike(f"%{lead_in.product_interest}%"))
    )
    product = prod_result.scalars().first()
    
    price = product.price if product else 1000.0
    product_name = product.name if product else lead_in.product_interest

    # 3. Trigger automated outbound SMS via Africa's Talking
    sms_message = (
        f"Hi {lead_in.name}! Thank you for inquiring about {product_name}. "
        f"Reply 1 to order at KES {price} with instant M-Pesa checkout."
    )
    await africastalking_service.send_sms(
        phone_number=lead_in.phone_number,
        message=sms_message
    )

    return lead
