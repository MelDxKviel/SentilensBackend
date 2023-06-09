from fastapi import FastAPI
import nltk

from app.database import init_db
from app.routers import note_router, hashtag_router, user_router
from app.config import global_settings


app = FastAPI(
    title="Sentilens API",
    description="API for Sentilens mobile app",
    version="0.1.2",
)

app.include_router(note_router)
app.include_router(hashtag_router)
app.include_router(user_router)


@app.on_event("startup")
async def startup():
    init_db()
    nltk.download('vader_lexicon')


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=global_settings.host, port=8000)
