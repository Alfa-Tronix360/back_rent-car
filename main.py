from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import database, models
from seed import seed
from routers import auth_router, veiculos, clientes, alugueres, pagamentos, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas e popula com dados iniciais (se estiver vazia)
    models.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Rent-a-Car API",
    description="API de gestão de aluguer de veículos",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://front-rent-a-car-self.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(veiculos.router)
app.include_router(clientes.router)
app.include_router(alugueres.router)
app.include_router(pagamentos.router)
app.include_router(dashboard.router)


@app.get("/", tags=["root"])
def root():
    return {"mensagem": "Rent-a-Car API a funcionar", "docs": "/docs"}


@app.get("/health", tags=["root"])
def health():
    return {"status": "ok"}
