import asyncio
import time
from functools import lru_cache
from typing import List, Tuple

from langchain.agents import create_agent
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import settings


SYSTEM_PROMPT = (
    "Você é um assistente responsável por gerar resumos de textos enviados pelo usuário. "
    "Construa o resumo com coerência, utilizando as informações mais importantes do texto "
    "e sem perder o contexto. "
    "Utilize apenas as informações e contextos presentes no texto enviado, "
    "não invente informações nem utilize outras fontes."
)

_llm_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_LLM_CALLS)


@lru_cache(maxsize=1)
def _get_agent():
    """Cria o agente uma única vez e reutiliza entre requisições
    (evita recriar modelo/agent a cada chamada)."""
    model = ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
    )
    return create_agent(model, system_prompt=SYSTEM_PROMPT)

def load_pdf_document(file_path: str) -> List[Document]:
    """Carrega um PDF e retorna uma lista de Document, cada um representando uma página."""
    print(file_path)
    loader = PyPDFLoader(file_path)
    return loader.load()

def split_into_chunks(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        add_start_index=True,
    )
    return splitter.split_documents(docs)


def group_chunks(chunks: List[Document], group_size: int = None) -> List[List[Document]]:
    group_size = group_size or settings.CHUNKS_PER_GROUP
    return [chunks[i : i + group_size] for i in range(0, len(chunks), group_size)]


async def _invoke_agent(content: str) -> str:
    agent = _get_agent()
    async with _llm_semaphore:
        try:
            resposta = await agent.ainvoke(
                {"messages": [{"role": "user", "content": content}]}
            )
        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Falha ao chamar o modelo: {exc}") from exc
    return resposta["messages"][-1].content


async def _summarize_group(group: List[Document]) -> str:
    texto = "\n\n".join(chunk.page_content for chunk in group)
    prompt = (
        "Resuma o conjunto de trechos abaixo.\n"
        "Mantenha apenas as informações importantes.\n\n"
        f"{texto}"
    )
    return await _invoke_agent(prompt)


async def _combine_summaries(summaries: List[str]) -> str:
    if len(summaries) == 1:
        # Já é um resumo único e coeso, não precisa de uma segunda passada.
        return summaries[0]

    join_summaries = "\n\n".join(summaries)
    prompt = (
        "A seguir estão vários resumos de partes do mesmo documento.\n"
        "Produza um único resumo coeso, eliminando repetições e mantendo "
        "apenas as informações importantes.\n\n"
        f"{join_summaries}"
    )
    return await _invoke_agent(prompt)


async def summarize_document(doc_path: str) -> Tuple[str, int]:
    """Executa o pipeline map-reduce para um único documento (uma lista de páginas).
    Retorna (resumo_final, numero_de_chunks)."""
    docs = load_pdf_document(doc_path)
    chunks = split_into_chunks(docs)
    groups = group_chunks(chunks)

    partial_summaries = await asyncio.gather(
        *(_summarize_group(group) for group in groups)
    )
    final_summary = await _combine_summaries(list(partial_summaries))
    return final_summary, len(chunks)


async def combine_documents_summaries(individual_summaries: List[str]) -> str:
    """Combina resumos já prontos de múltiplos documentos diferentes
    em um único resumo consolidado (usado no modo 'combined' do lote)."""
    return await _combine_summaries(individual_summaries)


def time_it_start() -> float:
    return time.perf_counter()


def time_it_elapsed(start: float) -> float:
    return round(time.perf_counter() - start, 2)