from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing import Union
import datetime

class SenderReceiverInfo(TypedDict):
    name: str
    street_address: str
    city: str
    country_code: str

class OrderRequest(BaseModel):
    sender: SenderReceiverInfo
    recipient: SenderReceiverInfo
    value: float
    despatch_date: datetime.date
    contents_declaration: str = Field(..., alias="contents declaration")
    insurance_required: bool
    tracking_reference: str

class OrderResponse(BaseModel):
    package: OrderRequest
    order_url: str
    accepted_at: Union[datetime.datetime, str]
    insurance_provided: bool
    total_insurance_charge: float
    ipt_included_in_charge: float
