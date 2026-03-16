# Stock NLT

Aplicação básica para inventário com front-end (React + Vite) e back-end (FastAPI + PostgreSQL + Celery/RabbitMQ).

---

## Pré-requisitos

- **Back-end:** Python 3.11+, PostgreSQL e RabbitMQ.
- **Front-end:** Node.js 18+ e npm (ou yarn/pnpm).
- **Docker + Docker compose:** Necessários pra produção. _Altamente recomendado para desenvolvimento_.

---

## Instalação

### Back-end

```bash
cd back-end
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Front-end

```bash
cd front-end
npm install
```

---

## Modo desenvolvimento (usando Docker para serviços externos)

### Back-end

1. Primeiro suba os serviços (Docker):

```bash
docker compose up
```

2. Depois inicialize o app em modo dev:

```bash
cd back-end
source .venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API: **http://localhost:8000**  
Docs: **http://localhost:8000/docs**

### Front-end

```bash
cd front-end
npm run dev
```

App: **http://localhost:8080**

O front usa a URL da API definida em `front-end/.env.local` (ou `.env.prod`).

---

## Testes (Back-end)

```bash
cd back-end
source .venv/bin/activate
pytest
```

Os testes de integração usam **Testcontainers** (Postgres).

Para rodar só testes de integração:

```bash
pytest tests/test_inventory_integration.py -v
```

---

## Produção (Docker Compose)

Sobe back-end, front-end, Postgres, RabbitMQ e worker Celery.

```bash
# Na raiz do repositório
docker compose --profile prod up --build
```

- **Front-end:** http://localhost:8080
- **Back-end (API):** http://localhost:8000

O front em prod é buildado com o arquivo `front-end/.env.prod` (modo `prod` do Vite). O Cors para esse endereço já está habilitado no back-end.

Para parar:

```bash
docker compose --profile prod down
```

---

## Variáveis de ambiente

### Back-end

O back-end lê variáveis de ambiente do sistema. Você pode definir em um arquivo `.env` na pasta `back-end/` e carregá-lo manualmente (ou com `python-dotenv` se adicionar ao projeto), ou exportar no shell.

| Variável                    | Descrição                              | Padrão                                                       |
| --------------------------- | -------------------------------------- | ------------------------------------------------------------ |
| `DATABASE_URL`              | URL de conexão PostgreSQL              | `postgresql://postgres:postgres@localhost:5432/database_nlt` |
| `CELERY_BROKER_URL`         | URL do broker (RabbitMQ) para Celery   | —                                                            |
| `SQL_ECHO`                  | Log de SQL (true/1 para ativar)        | `false`                                                      |
| `DB_CONNECT_MAX_RETRIES`    | Tentativas de conexão ao DB no startup | `30`                                                         |
| `DB_CONNECT_RETRY_INTERVAL` | Intervalo em segundos entre tentativas | `1.0`                                                        |

**Exemplo (Linux/macOS):**

```bash
cd back-end
export DATABASE_URL="postgresql://user:pass@localhost:5432/meudb"
export SQL_ECHO=true
uvicorn src.main:app --reload --port 8000
```

No **Docker Compose** (prod), `DATABASE_URL` e `CELERY_BROKER_URL` vêm do bloco `environment` do serviço `backend` em `docker-compose.yml`.
