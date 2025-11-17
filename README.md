# ERP Module – Inventory management

FastAPI-based ERP module that manages locations, inventory and transfer orders. Built with asynchronous SQLAlchemy, PostgreSQL, Redis-backed caching, and FastAPI Users for authentication/authorization.

---

## Contents
1. [Tech Stack](#tech-stack)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Requirements](#requirements)
5. [Environment Variables](#environment-variables)
6. [Setup & Installation](#setup--installation)
7. [Database & Migrations](#database--migrations)
8. [Running the App](#running-the-app)
9. [Caching](#caching)
10. [Admin Initialization](#admin-initialization)
11. [API Overview](#api-overview)

---

## Tech Stack

- **FastAPI** for REST API
- **SQLAlchemy 2.0 (async), AsyncPG** for database access
- **PostgreSQL** as the DB
- **Alembic** for schema migrations
- **Redis** (via `aiocache`) for response caching
- **FastAPI Users** for authentication, user management, and role-based access
- **Pydantic v2** for request/response validation
- **ELK Stack** for gathering, indexing and visualizing logs
- **Docker & Compose** for containerized development

---

## Features

### Authentication & Users
- FastAPI Users integration
- Role-based permissions (`ADMIN`, `MANAGER`, `SALESMAN`, `DELIVERY`, …)
- Startup hook initialises an admin user from environment variables

### Locations
- CRUD operations for locations (name, address, type)
- Optional caching layer on the “list all locations” endpoint
- Access control (only admins/managers can edit)

### Inventory (per Location)
- Store and manage stock using `location_products`
- Endpoints to list, fetch, create, update, delete inventory entries
- Adjust stock atomically (increment/decrement)
- Low-stock reporting (`stock < threshold`)
- Transfer inventory between locations with validation

### Orders (Inventory Transfers)
- Orders represent transfers between locations
- Orders contain product lines (`OrderProduct` items with quantity)
- Consumes/reserves stock at source when created/updated
- Releases stock to destination when delivered
- Full CRUD with nested products in responses

---

## Project Structure



---

## Requirements

- Docker & docker-compose
- Python 3.11+
- uv (preferred for speed) or Poetry (for Python dependency management)
- PostgreSQL
- Elastic Stack - Elasticsearch, Logstash, Kibana
- Redis
- Preferrably 16 Gb of RAM, or 8 Gb of RAM with a sufficiently large swap file

---

## Environment Variables

Create `.env` and `auth.env` file with environment variables used by the app.
Example `.env`:
```
DB_HOST="DB_HOST"
DB_PORT=0000
DB_NAME="DB_NAME"
DB_USER="DB_USER"
DB_PASS="DB_PASS"
LOGSTASH_HOST="LOGSTASH_HOST"
LOGSTASH_PORT=0000
REDIS_HOST="REDIS_HOST"
REDIS_PORT=0000
ADMIN_EMAIL="user@example.com"
ADMIN_PASS="Pass123!"
```
Example `auth.env`:
```
SECRET=SECRET
```
It is best to use something more secure than just `SECRET`.


## Setup & Installation
```
curl -LsSf https://astral.sh/uv/install.sh | sh # installs uv
git clone https://github.com/n-n06/highload-backend
cd highload-backend
uv sync
source .venv/bin/activate
uv run uvicorn src.main:app --reload #runs the app
```

## Database & Migrations

Generate migrations after schema changes:
```
alembic revision --autogenerate -m "description"
```
Apply migrations:
```
alembic upgrade head
```

`alembic/env.py` imports Base from src.db and loads all model modules before running.

## Run the app
### Local
```
uv run uvicorn src.main:app --reload #runs the app
```
The API docs will be at: http://127.0.0.1:8000/docs

### Docker
```yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    ports:
      - 9200:9200
    ...

  logstash:
    image: docker.elastic.co/logstash/logstash:8.15.0
    container_name: logstash
    depends_on:
      elasticsearch:
        condition: service_healthy
    ports:
      - 5044:5044
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.15.0
    container_name: kibana
    depends_on:
      elasticsearch:
        condition: service_healthy
    ports:
      - 5601:5601

  db:
    image: postgres:16
    restart: always
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASS}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    container_name: erp-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: ["redis-server", "--save", "60", "1", "--loglevel", "warning"]
    volumes:
      - redis-data:/data

  app:
    build: .
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"
    env_file:
      - .env
      - auth.env
    # volumes:
    #   - ./src:/app

volumes:
  pgdata:
  redis-data:
```

Start everything:
```bash
docker compose build
docker compose up -d
```

## Caching
- Uses aiocache with the Redis backend: cache=Cache.REDIS
- endpoint/port provided via settings (REDIS_HOST, REDIS_PORT)
- Namespace: "main", so keys appear as main:<hash>
- Serializer: PickleSerializer recommended when caching ORM objects or Pydantic models

Example cached endpoint:

```python
@cached(
    ttl=1000,
    cache=Cache.REDIS,
    endpoint=settings.redis_host,
    port=settings.redis_port,
    namespace="main",
    key_builder=make_key,
    serializer=PickleSerializer(),
)
@location_router.get("/", response_model=list[LocationRead])
async def list_all_locations(...):
    ...
```
Inspect keys inside the Redis container:

```bash
docker exec -it erp-redis redis-cli
127.0.0.1:6379> KEYS main:*
```

## Admin Initialization

The FastAPI lifespan hook auto-creates (or updates) an admin user using ADMIN_EMAIL/ADMIN_PASS:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        user_db_gen = get_user_db(session)
        user_db = await anext(user_db_gen)

        user_manager_gen = get_user_manager(user_db)
        user_manager = await anext(user_manager_gen)

        try:
            admin = await user_manager.get_by_email(settings.ADMIN_EMAIL)

            updated = False

            if not admin.is_superuser:
                admin.is_superuser = True
                updated = True
            if admin.role != UserRole.ADMIN:
                admin.role = UserRole.ADMIN
                updated = True

            if updated:
                await session.commit()
        except:
            user_create = UserCreate(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASS,
                role=UserRole.ADMIN,
                is_verified=True,
                is_superuser=True,
            )
            await user_manager.create(user_create, safe=False)
            await session.commit()
        finally:
            await user_manager_gen.aclose()
            await user_db_gen.aclose()

    yield

```
The admin is granted is_superuser=True and role ADMIN.

## API Overview
| Area | Endpoint | Method | Description | Permissions |
| :-- | :-- | :-- | :-- | :-- |
| Locations | /locations/ | POST | Create new location | Admin |
|  | /locations/ | GET | List locations (cached) | Authenticated |
|  | /locations/{id} | GET | Get location details (incl. inventory) | Authenticated |
|  | /locations/{id} | PUT | Update location | Admin |
|  | /locations/{id} | PATCH | Partial update | Admin |
|  | /locations/{id} | DELETE | Delete location | Superuser |
| Inventory | /locations/{loc_id}/products/ | GET | List inventory entries with product details | Authenticated |
|  | /locations/{loc_id}/products/{pid} | GET | Get single inventory record | Authenticated |
|  | /locations/{loc_id}/products/ | POST | Create inventory entry | Manager/Admin |
|  | /locations/{loc_id}/products/{pid} | PUT | Upsert inventory entry | Manager/Admin |
|  | /locations/{loc_id}/products/{pid} | PATCH | Adjust stock by delta | Manager/Admin |
|  | /locations/{loc_id}/products/{pid} | DELETE | Remove inventory record | Manager/Admin |
|  | /locations/{loc_id}/products/low-stock | GET | Products below threshold | Authenticated |
|  | /locations/{loc_id}/products/transfer | POST | Transfer stock to another location | Manager/Admin |
| Orders | /orders/ | POST | Create new transfer order (with product lines) | Manager |
|  | /orders/ | GET | List manager’s orders | Manager |
|  | /orders/{id} | GET | Retrieve order (manager or assigned delivery) | Manager/Delivery/Admin |
|  | /orders/{id} | PUT | Update order (replaces products, adjusts inventory) | Manager |
|  | /orders/{id}/deliver | POST | Mark delivered; adds stock to destination | Delivery person/Admin |

Authentication endpoints (/auth/login, /auth/register, etc.) provided by FastAPI Users (see src/auth/router.py).

