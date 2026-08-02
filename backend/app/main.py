from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth, search, alerts
from app.bot.main import bot, dp
from aiogram.types import Update

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")

@app.get("/")
@app.get("/health")
@app.get("/api")
@app.get("/api/health")
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}

@app.post("/api/v1/bot/webhook")
async def telegram_bot_webhook(request: Request):
    if not bot or not dp:
        return {"status": "bot token not configured"}
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path_name: str):
    return {"message": "Route caught by catch-all", "path": request.url.path, "path_name": path_name}
