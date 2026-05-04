from fastapi import FastAPI
from app.api.v1.endpoints import auth, users, chats

app = FastAPI(title="Speak Messenger")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(chats.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Speak API works"}