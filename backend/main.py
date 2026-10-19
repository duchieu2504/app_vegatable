"""
AgriDoc AI Backend - Main Application Entry Point.

This file only handles app setup, middleware, static files, and router registration.
All route logic is in api/routes/.
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes.diagnose import router as diagnose_router
from api.routes.encyclopedia import router as encyclopedia_router
from api.routes.admin import router as admin_router
from api.routes.history import router as history_router

app = FastAPI(title="AgriDoc AI Backend")

# CORS Configuration
# NOTE: In production, replace ["*"] with your actual frontend domain(s).
# Example: allow_origins=["https://your-app.com", "http://192.168.1.5:8081"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount dataset directory for serving disease images
os.makedirs("dataset", exist_ok=True)
app.mount("/dataset", StaticFiles(directory="dataset"), name="dataset")

# Register route modules
app.include_router(diagnose_router)
app.include_router(encyclopedia_router)
app.include_router(admin_router)
app.include_router(history_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to AgriDoc AI Backend"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
