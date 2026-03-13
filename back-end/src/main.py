from fastapi import FastAPI

from src.inventory import router as inventory_router

app = FastAPI()
app.include_router(inventory_router, prefix="/api")