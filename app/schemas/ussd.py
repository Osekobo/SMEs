from pydantic import BaseModel, Field

class USSDRequest(BaseModel):
    sessionId: str = Field(..., alias="sessionId")
    serviceCode: str = Field(..., alias="serviceCode")
    phoneNumber: str = Field(..., alias="phoneNumber")
    text: str = Field(default="", alias="text")

    class Config:
        populate_by_name = True
