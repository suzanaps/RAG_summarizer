import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from routes.router import api_router
from contextlib import asynccontextmanager



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#STATIC_DIR = os.path.join(BASE_DIR, "static")



app = FastAPI(title="Resumo de arquivos com RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


app.include_router(api_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)