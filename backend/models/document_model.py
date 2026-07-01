from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import List

from db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(1024), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    content_type: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="documents")
    summaries: Mapped[List["Summary"]] = relationship("Summary", back_populates="document", cascade="all, delete-orphan")
