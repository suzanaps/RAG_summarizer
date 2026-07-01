# RAG Summarizer — Backend

Esta é a base do backend da aplicação de resumo de documentos PDF utilizando RAG (Retrieval-Augmented Generation). O backend é construído com FastAPI, SQLAlchemy assíncrono e PostgreSQL.

## Requisitos
- Python 3.10+
- Docker e Docker Compose

## Setup de Desenvolvimento Local

### 1. Iniciar o Banco de Dados (PostgreSQL)
Suba o container do banco de dados local executando o seguinte comando na raiz do projeto:
```bash
docker compose up -d
```
Isso iniciará um container PostgreSQL executando na porta `5433` (mapeada para `5432` internamente) com os dados persistidos no volume `postgres_data`.

### 2. Configurar Variáveis de Ambiente
Copie o arquivo de exemplo de ambiente `.env.example` para `.env` na raiz do projeto:
```bash
cp .env.example .env
```
Ajuste as credenciais no arquivo `.env` se necessário:
- `DATABASE_USER=admin`
- `DATABASE_PASSWORD=admin_tca`
- `DATABASE_NAME=tca_chatbot`
- `DATABASE_HOST=localhost`
- `DATABASE_PORT=5433`

### 3. Instalar Dependências
Ative o seu ambiente virtual e instale as dependências listadas no `requirements.txt`:
```bash
.venv\Scripts\pip.exe install -r backend/requirements.txt
```

### 4. Executar o Servidor Backend
Inicie a aplicação executando:
```bash
.venv\Scripts\python.exe backend/main.py
```
Ao inicializar, a aplicação executará a função `init_models()` que cria automaticamente as tabelas `users`, `documents` e `summaries` no PostgreSQL (caso ainda não existam) usando o padrão `create_all()`.

---

## Estrutura do Banco de Dados (Modelos)

O banco de dados contém as seguintes tabelas e relacionamentos:
- **`users`**: Armazena dados dos usuários (email, senha criptografada).
- **`documents`**: Armazena metadados dos PDFs enviados (`filename`, `filepath`, `size_bytes`, `content_type`, `upload_date`), atrelado ao usuário (`user_id`).
- **`summaries`**: Armazena os resumos gerados a partir de um PDF (`content`, `created_at`), atrelado ao documento (`document_id`).

### Relacionamentos e Integridade (Cascading Delete):
- **User → Documentos (1-N)**: A deleção de um usuário remove automaticamente todos os seus documentos associados.
- **Documento → Resumos (1-N)**: A deleção de um documento remove automaticamente todos os seus resumos associados no banco.

---

## Testes Automatizados

Os testes integrados do banco de dados utilizam **SQLite em memória (`sqlite+aiosqlite`)** para garantir estabilidade e independência de serviços externos.
Para rodar os testes:
1. Instale as dependências de desenvolvimento:
   ```bash
   .venv\Scripts\pip.exe install pytest pytest-asyncio aiosqlite
   ```
2. Execute o comando de teste configurando o `PYTHONPATH`:
   ```bash
   # No PowerShell
   $env:PYTHONPATH="backend"; .venv\Scripts\pytest.exe backend/tests/test_database.py
   ```
