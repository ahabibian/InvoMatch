from fastapi import FastAPI
from invomatch.api.health import router as health_router

app = FastAPI(title='InvoMatch')

app.include_router(health_router)