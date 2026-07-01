# RAG Summarizer

Sistema de processamento de documentos com foco em sumarização por RAG (Retrieval-Augmented Generation). 

## O que a aplicação faz

Atualmente, a aplicação permite:

- criar autenticação de usuários com JWT;
- realizar login na API;
- enviar arquivos PDF para o servidor;
- salvar os arquivos em disco e registrar os metadados no banco de dados.

## Tecnologias utilizadas

- Python 3.11+
- FastAPI


## Requisitos

Antes de rodar a aplicação, certifique-se de ter instalado:

- Python 3.11 ou superior;
- pip ou uv.

## Como rodar

### 1. Entre na pasta do backend

```bash
cd backend
```

### 2. Crie e ative um ambiente virtual

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo chamado .env na raiz do projeto (na pasta RAG_summarizer) com conteúdo semelhante a este:

```env
SECRET_KEY=troque-esta-chave
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=rag_summarizer
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
```

> O projeto utiliza essas variáveis para configurar a conexão com o banco e a geração de tokens.

### 5. Inicie a aplicação

```bash
python main.py
```

Ou, se preferir:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API ficará disponível em:

- http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs

## Endpoints principais

### Autenticação

- POST /auth/login

### Documentos

- POST /documents/upload

> O endpoint de upload exige autenticação via token Bearer.

## Estrutura do projeto

```text
backend/
  main.py
  core/
  db/
  models/
  repositories/
  routes/
  schemas/
  services/
```

## Próximos passos

O projeto pode evoluir para incluir:

- indexação de documentos;
- busca semântica;
- geração de resumos com modelos de linguagem;
- interface web para interação com os documentos.
