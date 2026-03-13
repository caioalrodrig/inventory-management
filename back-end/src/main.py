from fastapi import FastAPI

from src.controller.inventory_controller import router as inventory_router

app = FastAPI()
app.include_router(inventory_router, prefix="/api")