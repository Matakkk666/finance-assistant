from datetime import date
from pydantic import BaseModel

class Transaction(BaseModel):
    date: date
    description: str
    amount: float
