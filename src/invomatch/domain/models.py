from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class Invoice(BaseModel):
    id:str
    date:date
    amount:Decimal

class Payment(BaseModel):
    id:str
    date:date
    amount:Decimal