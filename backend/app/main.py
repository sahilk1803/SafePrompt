from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import config
from app.api.routes import router

app = FastAPI(
    title=config.APP_NAME,
    description="Explainable, Privacy-Aware and Responsible Prompt Engineering Framework for Course 23CIE734 (MSRIT)",
    version=config.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for React frontend (Vite default port 5173 and 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(router)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {config.APP_NAME} API Backend",
        "course": f"{config.COURSE_CODE} - {config.COURSE_NAME}",
        "institution": config.INSTITUTION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
