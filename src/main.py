from fastapi import FastAPI

app = FastAPI(title="Finance Assistant API")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}
