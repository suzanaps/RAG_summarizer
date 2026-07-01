import pytest
import pytest_asyncio
from datetime import datetime, timezone
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.base import Base
from models.user_model import User
from models.document_model import Document
from models.summary_model import Summary
from repositories.document_repository import document_repo

# In-memory SQLite connection for testing database models and repositories
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_database_creation_and_relations():
    # 1. Create two test users in session 1
    async with TestingSessionLocal() as session:
        user_a = User(email="usera@example.com", hashed_password="hashedpassword123")
        user_b = User(email="userb@example.com", hashed_password="hashedpassword456")
        session.add_all([user_a, user_b])
        await session.commit()
        user_a_id = user_a.id
        user_b_id = user_b.id
        
        assert user_a_id is not None
        assert user_b_id is not None

    # Query User A in a new session to confirm 0 documents initially
    async with TestingSessionLocal() as session:
        stmt = select(User).where(User.id == user_a_id).options(selectinload(User.documents))
        result = await session.execute(stmt)
        queried_user_a = result.scalar_one()
        assert len(queried_user_a.documents) == 0

    # 2. Add documents to User A in session 2
    async with TestingSessionLocal() as session:
        doc_a1 = await document_repo.create(
            session,
            filename="documento1.pdf",
            filepath="/uploads/1/documento1.pdf",
            user_id=user_a_id,
            size_bytes=1024,
            content_type="application/pdf"
        )
        
        doc_a2 = await document_repo.create(
            session,
            filename="documento2.pdf",
            filepath="/uploads/1/documento2.pdf",
            user_id=user_a_id,
            size_bytes=2048,
            content_type="application/pdf"
        )
        doc_a1_id = doc_a1.id
        doc_a2_id = doc_a2.id
        
        # Ensure doc_a1 is newer than doc_a2 by setting manual dates and committing
        doc_a2.upload_date = datetime(2026, 6, 30, 10, 0, 0, tzinfo=timezone.utc)
        doc_a1.upload_date = datetime(2026, 6, 30, 11, 0, 0, tzinfo=timezone.utc)
        await session.commit()

    # 3. Add document to User B in session 3
    async with TestingSessionLocal() as session:
        doc_b = await document_repo.create(
            session,
            filename="documento_b.pdf",
            filepath="/uploads/2/documento_b.pdf",
            user_id=user_b_id,
            size_bytes=4096,
            content_type="application/pdf"
        )
        doc_b_id = doc_b.id

    # 4. Check User -> Documents relationships in session 4
    async with TestingSessionLocal() as session:
        stmt = select(User).where(User.id == user_a_id).options(selectinload(User.documents))
        result = await session.execute(stmt)
        queried_user_a = result.scalar_one()
        assert len(queried_user_a.documents) == 2
        filenames = [d.filename for d in queried_user_a.documents]
        assert "documento1.pdf" in filenames
        assert "documento2.pdf" in filenames

    # 5. Check Document Repository List, Isolation and Ordering in session 5
    async with TestingSessionLocal() as session:
        docs_a = await document_repo.list_by_user(session, user_id=user_a_id)
        assert len(docs_a) == 2
        
        # Verify ordering: list_by_user sorts by upload_date DESC (newest first)
        assert docs_a[0].id == doc_a1_id
        assert docs_a[1].id == doc_a2_id
        
        # Verify count
        count_a = await document_repo.count_by_user(session, user_id=user_a_id)
        assert count_a == 2

        # Isolation check for B
        docs_b = await document_repo.list_by_user(session, user_id=user_b_id)
        assert len(docs_b) == 1
        assert docs_b[0].id == doc_b_id

    # 6. Add summary to Document A1 in session 6
    async with TestingSessionLocal() as session:
        summary = Summary(content="Resumo gerado com sucesso.", document_id=doc_a1_id)
        session.add(summary)
        await session.commit()
        summary_id = summary.id

    # Verify document relationship with summaries in session 7
    async with TestingSessionLocal() as session:
        stmt_doc = select(Document).where(Document.id == doc_a1_id).options(selectinload(Document.summaries))
        res_doc = await session.execute(stmt_doc)
        queried_doc_a1 = res_doc.scalar_one()
        assert len(queried_doc_a1.summaries) == 1
        assert queried_doc_a1.summaries[0].content == "Resumo gerado com sucesso."

    # 7. Check Cascade delete: Delete Document A1, summary should be deleted in session 8
    async with TestingSessionLocal() as session:
        doc_to_delete = await document_repo.get(session, doc_a1_id)
        await document_repo.delete(session, doc_to_delete)
        
    async with TestingSessionLocal() as session:
        stmt_sum = select(Summary).where(Summary.document_id == doc_a1_id)
        res_sum = await session.execute(stmt_sum)
        assert res_sum.scalar_one_or_none() is None

    # 8. Check Cascade delete: Delete User B, document B should be deleted in session 9
    async with TestingSessionLocal() as session:
        user_to_delete = await session.get(User, user_b_id)
        await session.delete(user_to_delete)
        await session.commit()
        
    async with TestingSessionLocal() as session:
        stmt_doc = select(Document).where(Document.user_id == user_b_id)
        res_doc = await session.execute(stmt_doc)
        assert res_doc.scalar_one_or_none() is None
