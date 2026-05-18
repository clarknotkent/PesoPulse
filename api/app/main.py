from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_firebase_app
from app.routes import auth, transactions, categories, receipts, sharing

get_firebase_app()

app = FastAPI(title="PesoPulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["receipts"])
app.include_router(sharing.router, prefix="/api/sharing", tags=["sharing"])


@app.get("/api/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok", "service": "PesoPulse API"}
