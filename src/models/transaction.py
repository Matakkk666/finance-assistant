import datetime
from pydantic import BaseModel


class Transaction(BaseModel):
    date: datetime.date
    description: str
    amount: float
