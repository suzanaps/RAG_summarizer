import os
import tempfile
import pytest
import pytest_asyncio
import shutil
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from db.base import Base
from main import app
from db.database import get_db
from models.document_model import Document

# SQLite in-memory database setup for testing endpoints
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

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# Override the database dependency in the FastAPI application
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_document_listing_and_download_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Register User A
        reg_a = await ac.post("/auth/register", json={
            "email": "usera@example.com",
            "password": "password123"
        })
        assert reg_a.status_code == 201
        token_a = reg_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 2. Register User B
        reg_b = await ac.post("/auth/register", json={
            "email": "userb@example.com",
            "password": "password123"
        })
        assert reg_b.status_code == 201
        token_b = reg_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 3. List documents User A (must be empty list)
        list_res = await ac.get("/documents", headers=headers_a)
        assert list_res.status_code == 200
        data = list_res.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["limit"] == 10

        # 4. Access listing without token (must return 401 Unauthorized)
        no_auth_res = await ac.get("/documents")
        assert no_auth_res.status_code == 401

        # 5. Create a temporary PDF file to upload
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"%PDF-1.4 dummy contents")
            tmp_path = tmp.name

        try:
            # Upload document for User A
            with open(tmp_path, "rb") as f:
                upload_res = await ac.post(
                    "/documents/upload",
                    headers=headers_a,
                    files={"file": ("relatorio.pdf", f, "application/pdf")}
                )
            assert upload_res.status_code == 200
            doc_id = upload_res.json()["id"]

            # 6. List documents User A again (must contain 1 item)
            list_res_a = await ac.get("/documents", headers=headers_a)
            assert list_res_a.status_code == 200
            data_a = list_res_a.json()
            assert len(data_a["items"]) == 1
            assert data_a["items"][0]["id"] == doc_id
            assert data_a["items"][0]["filename"] == "relatorio.pdf"
            assert data_a["items"][0]["size_bytes"] > 0
            assert data_a["items"][0]["content_type"] == "application/pdf"
            assert data_a["total"] == 1

            # 7. List documents User B (isolation check - must remain empty)
            list_res_b = await ac.get("/documents", headers=headers_b)
            assert list_res_b.status_code == 200
            data_b = list_res_b.json()
            assert len(data_b["items"]) == 0
            assert data_b["total"] == 0

            # 8. Pagination query parameter validation check (must return 422 Validation Error)
            invalid_page_res = await ac.get("/documents?page=0", headers=headers_a)
            assert invalid_page_res.status_code == 422
            
            invalid_limit_res = await ac.get("/documents?limit=101", headers=headers_a)
            assert invalid_limit_res.status_code == 422

            # 9. Download own document (must return 200 OK and correct binary stream)
            download_res_a = await ac.get(f"/documents/{doc_id}", headers=headers_a)
            assert download_res_a.status_code == 200
            assert download_res_a.content == b"%PDF-1.4 dummy contents"

            # 10. Access check: User B attempting to download User A's document (must return 403 Forbidden)
            download_res_b = await ac.get(f"/documents/{doc_id}", headers=headers_b)
            assert download_res_b.status_code == 403

        finally:
            # Clean up local temporary file and uploads directory created by testing
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
            if os.path.exists(uploads_dir):
                shutil_dir = os.path.abspath(uploads_dir)
                shutil.rmtree(shutil_dir, ignore_errors=True)
