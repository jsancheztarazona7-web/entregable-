from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import products, providers, quotes
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QuotePro API",
    description="Sistema de Cotizaciones",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(providers.router)
app.include_router(quotes.router)

@app.get("/")
def root():
    return {"message": "QuotePro API funcionando ✅", "version": "1.0.0"}