from fastapi import FastAPI

app = FastAPI(title="Speak Messenger")

@app.get("/")
async def root():
    return {"message": "Speak API works"}