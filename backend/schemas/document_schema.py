from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class DocumentResponse(BaseModel):
    id: int
    filename: str
    user_id: int
    upload_date: datetime

    class Config:
        from_attributes = True

class DocumentItem(BaseModel):
    id: int
    filename: str
    size_bytes: Optional[int]
    content_type: Optional[str]
    upload_date: datetime

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    items: List[DocumentItem]
    page: int
    limit: int
    total: int
