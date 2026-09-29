from fastapi import FastAPI

app = FastAPI(title="Lyra")

@app.get("/")
async def root():
    return {
        "name": "Lyra",
        "status": "online"
    }

@app.get("/health")
async def health():
    return {
        "lyra": "online"
    }