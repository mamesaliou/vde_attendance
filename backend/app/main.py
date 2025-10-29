from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.database import engine, Base
from .routes import students, attendance, stage

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="School Attendance API",
    description="Système de gestion des présences scolaire",
    version="1.0.0"
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
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])
app.include_router(stage.router, prefix="/api/classes", tags=["stages"])

@app.get("/")
async def root():
    return {"message": "School Attendance API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}