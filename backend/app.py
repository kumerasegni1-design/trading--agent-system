from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager

from config import settings, logger
from orchestrator.coordinator import AgentCoordinator
from routes import agents, backtesting, strategies, models, marketplace

# Initialize coordinator
coordinator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    global coordinator
    logger.info("🚀 Starting Trading Agent System...")
    
    # Initialize coordinator on startup
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    logger.info("✅ Coordinator initialized")
    
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down Trading Agent System...")
    await coordinator.shutdown()
    logger.info("✅ Coordinator shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Trading Agent System API",
    description="Multi-agent orchestration for trading strategy generation, backtesting, and deployment",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(backtesting.router, prefix="/api/backtesting", tags=["Backtesting"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])
app.include_router(models.router, prefix="/api/models", tags=["ML Models"])
app.include_router(marketplace.router, prefix="/api/marketplace", tags=["Marketplace"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Trading Agent System",
        "status": "online",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "coordinator": "initialized" if coordinator else "not_initialized"
    }

@app.websocket("/ws/command")
async def websocket_command(websocket: WebSocket):
    """WebSocket for real-time command dispatch and agent communication"""
    await websocket.accept()
    logger.info(f"🔌 WebSocket client connected")
    
    try:
        while True:
            data = await websocket.receive_json()
            logger.info(f"📨 Received command: {data.get('type', 'unknown')}")
            
            # Dispatch to coordinator
            result = await coordinator.dispatch_command(data)
            
            # Send response back
            await websocket.send_json(result)
    
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {str(e)}")
        await websocket.close(code=1000)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
