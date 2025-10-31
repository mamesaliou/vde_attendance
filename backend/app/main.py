from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .database.database import engine, Base
# from .routes import students, classes, attendance, reports
from .auth.route import router as auth_router
from .config import settings

# Créer les tables seulement en production, pas pendant les tests
if not os.getenv("TESTING"):
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="School Attendance API",
    description="Système complet de gestion des présences scolaire avec authentification",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])


@app.get("/")
async def root():
    return {
        "message": "School Attendance Management System",
        "version": "3.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}