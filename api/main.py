from fastapi import FastAPI

from .middlewares import applyCors
from .features import verifai_router

app = FastAPI(
    root_path="/api"
)

applyCors(app)


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router=verifai_router)