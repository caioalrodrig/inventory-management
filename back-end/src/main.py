from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import create_tables, wait_for_db
from src.inventory import router as inventory_router


# makes DB available before FastAPI startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(inventory_router, prefix="/api")
