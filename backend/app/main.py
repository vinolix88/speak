from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, users, chats
from app.api.v1.endpoints import search
from app.api.v1.endpoints.websocket import websocket_chat

app = FastAPI(title="Speak Messenger")

# Разрешаем запросы с любых источников (для тестирования)
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"  # на время разработки можно открыть полностью
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(chats.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.add_api_websocket_route("/ws/chat/{chat_id}", websocket_chat)

@app.get("/")
async def root():
    return {"message": "Speak API works"}