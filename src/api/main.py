from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.database.connection import init_database
from .routes import instructors, courses, locations, ratings, sessions, assignments, auth
from .middleware.error_handler import add_error_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - only init database if not in test mode
    if not os.getenv("TESTING"):
        init_database()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Instructor Scheduling API",
    description="API for managing instructor scheduling, courses, and assignments",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handlers
add_error_handlers(app)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(instructors.router, prefix="/api/v1/instructors", tags=["instructors"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(ratings.router, prefix="/api/v1/ratings", tags=["ratings"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(assignments.router, prefix="/api/v1/assignments", tags=["assignments"])

@app.get("/")
async def root():
    return {"message": "Instructor Scheduling API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)