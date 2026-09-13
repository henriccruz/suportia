"""Ponto de entrada da aplicação FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, SessionLocal, User
from app.auth import hash_password
from app.routes import router

app = FastAPI(title="SuportIA API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    # Criar usuário admin padrão se não existir
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin_user = User(username="admin", hashed_password=hash_password("admin"))
        db.add(admin_user)
        db.commit()
    db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
