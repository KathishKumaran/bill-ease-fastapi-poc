import asyncio
import uvicorn
from fastapi import FastAPI
from models.models import Base
from config.logger import logger
from config.database import engine
from fastapi.middleware.cors import CORSMiddleware
from modules.routers import router as modules_router
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers = ['*'],
    allow_credentials=True,
)

app.include_router(modules_router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
def shutdown():
    engine.dispose()
    logger.info("Application shutting down")

async def main():
    host = "0.0.0.0"
    port = 3000
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    logger.info(f"Server listening at http://{host}:{port}")  # Log the server startup message
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
