import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from models.user_model import User
from schemas.document_schema import DocumentResponse
from repositories.document_repository import document_repo
from services.auth_service import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Formato de arquivo invalido. Apenas arquivos PDF sao permitidos.")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="A extensao do arquivo deve ser .pdf.")

    # In newer FastAPI versions, file.size is available.
    # We fallback to seeking the end of the file if size is None.
    file_size = file.size
    if file_size is None:
        # Seek to the end to get the size
        await file.seek(0, 2)
        file_size = file.file.tell()
        await file.seek(0)
        
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="O tamanho do arquivo excede o limite de 50MB.")

    # Create user-specific upload directory
    user_upload_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)

    # Secure filename with UUID to avoid collision
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(user_upload_dir, unique_filename)

    # Save to disk
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save to database
    document = await document_repo.create(
        session=db,
        filename=file.filename,
        filepath=filepath,
        user_id=current_user.id,
        size_bytes=file_size,
        content_type=file.content_type
    )

    return document
