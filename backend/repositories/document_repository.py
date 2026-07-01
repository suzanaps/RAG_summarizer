from models.document_model import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Iterable, Optional


class DocumentRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        filename: str,
        filepath: str,
        user_id: int,
        size_bytes: Optional[int] = None,
        content_type: Optional[str] = None
    ) -> Document:
        document = Document(
            filename=filename,
            filepath=filepath,
            user_id=user_id,
            size_bytes=size_bytes,
            content_type=content_type
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        return document

    async def get(self, session: AsyncSession, document_id: int) -> Optional[Document]:
        return await session.get(Document, document_id)

    async def list_by_user(self, session: AsyncSession, user_id: int, skip: int = 0, limit: int = 50) -> Iterable[Document]:
        query = select(Document).where(Document.user_id == user_id).order_by(Document.upload_date.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def count_by_user(self, session: AsyncSession, user_id: int) -> int:
        query = select(func.count(Document.id)).where(Document.user_id == user_id)
        result = await session.execute(query)
        return result.scalar() or 0

    async def delete(self, session: AsyncSession, document: Document) -> None:
        await session.delete(document)
        await session.commit()


document_repo = DocumentRepository()
