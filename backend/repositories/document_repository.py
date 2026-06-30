from models.document_model import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Iterable, Optional


class DocumentRepository:
    async def create(self, session: AsyncSession, *, filename: str, filepath: str, user_id: int) -> Document:
        document = Document(
            filename=filename,
            filepath=filepath,
            user_id=user_id
        )
        session.add(document)
        session.commit()
        session.refresh(document)
        return document

    async def get(self, session: AsyncSession, document_id: int) -> Optional[Document]:
        return await session.get(Document, document_id)

    async def list_by_user(self, session: AsyncSession, user_id: int, skip: int = 0, limit: int = 50) -> Iterable[Document]:
        query = select(Document).where(Document.user_id == user_id).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def delete(self, session: AsyncSession, document: Document) -> None:
        await session.delete(document)
        await session.commit()


document_repo = DocumentRepository()
