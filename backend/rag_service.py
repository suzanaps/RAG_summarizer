from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

import os
from dotenv import load_dotenv

#COLOCAR O LIMITE PRO RESUMO (CARACTERES, PAGINA) e ver tempo de geracao de resumo
#carregamento do texto

loader = PyPDFLoader("documents/teste.pdf")

docs = loader.load()

#print(docs[2].page_content[:500])

#chunking

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
chunks = text_splitter.split_documents(docs)

def agrupar_chunks(chunks, tamanho_grupo=5):
    grupos = []

    for i in range(0, len(chunks), tamanho_grupo):
        grupos.append(chunks[i:i+tamanho_grupo])

    return grupos

#print(f"Split into {len(chunks)} sub-documents.")

#resumo dos chunks

groups = agrupar_chunks(chunks=chunks)

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

prompt = (
    "Você é um assistente responsável por gerar resumos de textos enviados pelo usuário. "
    "Construa o resumo com coerência utilizando as informações mais importantes do texto e sem perder o contexto  "
    "Utilize apenas as informações e contextos presentes no texto enviado, não invente informações ou utilize outras fontes"
)
agent = create_agent(model, system_prompt=prompt)

resumos = []

for grupo in groups:

    texto = "\n\n".join(
        chunk.page_content
        for chunk in grupo
    )

    resposta = agent.invoke({
        "messages": [
            {
            "role": "user",
            "content": f"""
            Resuma o conjunto de trechos abaixo.
            Mantenha apenas as informações importantes.
            {texto}
            """
            }
        ]
    })

    resumos.append(resposta["messages"][-1].content)

join_summaries= "\n\n".join(resumos)


final_summary = agent.invoke({
    "messages":[
        {
             "role": "user",
             "content": f"""
                A seguir estão vários resumos de partes do mesmo documento.
                Produza um único resumo coeso,
                eliminando repetições e mantendo
                apenas as informações importantes.
                {join_summaries}
                """
        }
    ] })

print(final_summary)




