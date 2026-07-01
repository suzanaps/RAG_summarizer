import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
from routes.router import api_router
from contextlib import asynccontextmanager
from db.database import init_models
from models.document_model import Document
from models.user_model import User
from models.summary_model import Summary

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#STATIC_DIR = os.path.join(BASE_DIR, "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield

app = FastAPI(title="Resumo de arquivos com RAG", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


app.include_router(api_router)


#os.makedirs(STATIC_DIR, exist_ok=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)