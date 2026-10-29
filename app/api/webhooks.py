from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.lead import Lead
from app.models.product import Product
from app.schemas.lead import MetaLeadRequest, LeadResponse

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

@router.post("/meta-leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def meta_leads_webhook(lead_in: MetaLeadRequest, db: AsyncSession = Depends(get_db)):
    """
    Accepts Meta (Facebook/Instagram) Lead Ads webhook payload and creates a Lead record.
    """
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

    return lead
