from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from core.config import settings
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.document_repository import document_repo
from schemas.summary_schema import (
    BatchMode,
    BatchSummaryResponse,
    FileSummaryResult,
    SingleSummaryResponse,
)

from services.rag_service import (
    combine_documents_summaries,
    summarize_document,
    time_it_elapsed,
    time_it_start,
)

router = APIRouter(prefix="/api/summarize", tags=["summarize"])


async def _summarize_single_file(file_id: int, db: AsyncSession) -> FileSummaryResult:
    start = time_it_start()
    docs = await document_repo.get(db, file_id)
    summary, num_chunks = await summarize_document(docs.filepath)
    return FileSummaryResult(
        filename=docs.filename,
        num_chunks=num_chunks,
        summary=summary,
        processing_time_seconds=time_it_elapsed(start),
    )


@router.post("", response_model=SingleSummaryResponse)
async def summarize_single(file_id: int, db: AsyncSession = Depends(get_db)):
    """Resume um único arquivo PDF."""
    result = await _summarize_single_file(file_id, db)

    if not result.summary:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Falha ao gerar o resumo do arquivo.",
        )
   

    return SingleSummaryResponse(result=result)


@router.post("/batch", response_model=BatchSummaryResponse)
async def summarize_batch(
    files: List[UploadFile] = File(...),
    mode: BatchMode = Query(
        default=BatchMode.INDIVIDUAL,
        description=(
            "individual: um resumo por arquivo. "
            "combined: um resumo por arquivo + um resumo único consolidando todos."
        ),
    ),
):
    """Resume múltiplos arquivos PDF, individualmente ou de forma combinada,
    de acordo com a escolha do usuário (query param `mode`)."""

    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    if len(files) > settings.MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Número de arquivos ({len(files)}) excede o limite de "
                f"{settings.MAX_FILES_PER_REQUEST} por requisição."
            ),
        )

    total_start = time_it_start()
    results: List[FileSummaryResult] = []
    errors: List[str] = []

    for file in files:
        try:
            result = await _summarize_single_file(file)
            results.append(result)
        except Exception as exc:
            errors.append(f"{file.filename}: {exc}")

    if not results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nenhum arquivo pôde ser processado. Erros: {'; '.join(errors)}",
        )

    combined_summary = None
    if mode == BatchMode.COMBINED:
        try:
            combined_summary = await combine_documents_summaries(
                [r.summary for r in results]
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
            ) from exc

    # Arquivos que falharam não derrubam a requisição inteira; ficam
    # reportados em partial_errors para o cliente decidir o que fazer.
    return BatchSummaryResponse(
        mode=mode,
        files=results,
        combined_summary=combined_summary,
        total_processing_time_seconds=time_it_elapsed(total_start),
        partial_errors=errors,
    )