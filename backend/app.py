import asyncio
import json
import logging
import os
import sys
from collections import deque
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, File, UploadFile, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import asyncpg

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.onnx_pipeline import VoicePipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fallback in-memory session cache when Redis is unavailable (e.g. standalone test mode)
memory_sessions: dict[str, deque[float]] = {}
redis_client = None
db_pool = None
pipeline = VoicePipeline()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, db_pool

    # Read configuration from environment with defaults
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = int(os.getenv("POSTGRES_PORT", "5432"))
    pg_user = os.getenv("POSTGRES_USER", "avc")
    pg_password = os.getenv("POSTGRES_PASSWORD", "avcpassword")
    pg_db = os.getenv("POSTGRES_DB", "avcdb")

    # Connect to Redis
    try:
        client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        await client.ping()
        redis_client = client
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.warning(f"Redis unavailable ({e}). Using in-memory rolling window cache.")
        redis_client = None

    # Connect to PostgreSQL
    try:
        db_pool = await asyncpg.create_pool(
            user=pg_user, password=pg_password, database=pg_db, host=pg_host, port=pg_port,
            timeout=2.0
        )
        async with db_pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT,
                    score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        logger.info("Connected to PostgreSQL successfully.")
    except Exception as e:
        logger.warning(f"Database connection failed ({e}). Running without telemetry persistence.")
        db_pool = None

    yield

    # Teardown
    if redis_client:
        try:
            await redis_client.aclose()
        except Exception:
            pass
    if db_pool:
        try:
            await db_pool.close()
        except Exception:
            pass

app = FastAPI(
    title="AvC - Audio Deepfake & Synthesis Detector",
    description="Real-time detection engine & cybersecurity telemetry for voice clone impersonation attacks",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AvC Audio Deepfake Detector",
        "version": "1.0.0",
        "redis_connected": redis_client is not None,
        "database_connected": db_pool is not None
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        max_score, heatmap_b64 = pipeline.process_full_audio_file(content)
        
        # Log this file analysis to postgres if connected
        if db_pool:
            try:
                async with db_pool.acquire() as conn:
                    await conn.execute(
                        "INSERT INTO logs (session_id, score) VALUES ($1, $2)",
                        "file_upload", max_score
                    )
            except Exception as e:
                logger.error(f"Failed to log file analysis to database: {e}")
                
        return {
            "score": max_score,
            "heatmap": f"data:image/png;base64,{heatmap_b64}"
        }
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return {"error": str(e)}

@app.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()
    session_id = str(id(websocket))
    logger.info(f"Session {session_id} connected")
    try:
        while True:
            # Receive raw PCM bytes
            data = await websocket.receive_bytes()
            
            # 1. AI Pipeline Processing
            score = pipeline.process_chunk(data)
            
            # 2. Explainability Heatmap
            heatmap_b64 = pipeline.generate_spectrogram(data)
            
            # 3. Rolling Window (Redis with in-memory fallback)
            scores = []
            if redis_client:
                try:
                    redis_key = f"session:{session_id}:scores"
                    await redis_client.rpush(redis_key, score)
                    await redis_client.ltrim(redis_key, -10, -1)
                    scores_str = await redis_client.lrange(redis_key, 0, -1)
                    scores = [float(s) for s in scores_str]
                except Exception as e:
                    logger.warning(f"Redis operation error: {e}")

            if not scores:
                if session_id not in memory_sessions:
                    memory_sessions[session_id] = deque(maxlen=10)
                memory_sessions[session_id].append(score)
                scores = list(memory_sessions[session_id])
            
            agg_score = sum(scores) / len(scores) if scores else score
            
            # 4. PostgreSQL Logging if connected
            if db_pool:
                try:
                    async with db_pool.acquire() as conn:
                        await conn.execute(
                            "INSERT INTO logs (session_id, score) VALUES ($1, $2)",
                            session_id, agg_score
                        )
                except Exception as e:
                    logger.error(f"Failed to log score to database: {e}")
            
            # 5. Send result to frontend
            await websocket.send_json({
                "score": float(score), 
                "agg_score": float(agg_score),
                "heatmap": f"data:image/png;base64,{heatmap_b64}"
            })
            
    except WebSocketDisconnect:
        logger.info(f"Session {session_id} disconnected")
        if redis_client:
            try:
                await redis_client.delete(f"session:{session_id}:scores")
            except Exception:
                pass
        memory_sessions.pop(session_id, None)
