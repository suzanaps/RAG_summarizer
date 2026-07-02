from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class BatchMode(str, Enum):
    """Modo de resumo para múltiplos arquivos.

    - individual: gera um resumo separado para cada PDF enviado.
    - combined: gera um resumo por PDF e depois um resumo único
      que consolida o conteúdo de todos os documentos.
    """

    INDIVIDUAL = "individual"
    COMBINED = "combined"


class FileSummaryResult(BaseModel):
    filename: str
    num_chunks: int
    summary: str
    processing_time_seconds: float


class SingleSummaryResponse(BaseModel):
    result: FileSummaryResult


class BatchSummaryResponse(BaseModel):
    mode: BatchMode
    files: List[FileSummaryResult]
    combined_summary: Optional[str] = Field(
        default=None,
        description="Preenchido apenas quando mode='combined'.",
    )
    total_processing_time_seconds: float
    partial_errors: List[str] = Field(
        default_factory=list,
        description="Arquivos que falharam ao processar (se houver), com a respectiva mensagem de erro.",
    )


class ErrorDetail(BaseModel):
    filename: Optional[str] = None
    error: str