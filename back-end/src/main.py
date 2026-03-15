from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import create_tables
from src.inventory import router as inventory_router


# makes DB available before FastAPI startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(inventory_router, prefix="/api")
