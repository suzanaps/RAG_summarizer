from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    user_id: int
    upload_date: datetime

    class Config:
        from_attributes = True
