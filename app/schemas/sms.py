from pydantic import BaseModel, Field

class InboundSMSRequest(BaseModel):
    date: str | None = None
    id: str | None = None
    linkId: str | None = None
    text: str
    from_: str = Field(..., alias="from")
    to: str | None = None

    class Config:
        populate_by_name = True
