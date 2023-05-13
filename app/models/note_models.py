from datetime import datetime
from typing import Optional
import uuid as uuid_pkg

from sqlmodel import SQLModel, Field, Relationship

from app.models.sentiment_models import Sentiment, SentimentReadWithAdvices


class NoteHashtagLink(SQLModel, table=True):
    note_uuid: uuid_pkg.UUID = Field(default=None, foreign_key="note.uuid", primary_key=True)
    hashtag_uuid: uuid_pkg.UUID = Field(default=None, foreign_key="hashtag.uuid", primary_key=True)


class NoteBase(SQLModel):
    title: str
    content: str


class Note(NoteBase, table=True):
    uuid: Optional[uuid_pkg.UUID] = Field(default_factory=uuid_pkg.uuid4, primary_key=True, index=True, nullable=False)
    mood_value: float = Field(default=0)
    owner_id: int = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    sentiment_id: str = Field(default='Нейтральное', foreign_key="sentiment.title")
    sentiment: Sentiment = Relationship()
    hashtags: list["Hashtag"] = Relationship(back_populates="notes", link_model=NoteHashtagLink)


class NoteRead(NoteBase):
    uuid: uuid_pkg.UUID
    created_at: datetime
    updated_at: datetime

    sentiment: SentimentReadWithAdvices = None


class NoteReadWithHashtags(NoteRead):
    created_at: datetime
    updated_at: datetime
    hashtags: list["HashtagRead"] = []


class NoteCreate(NoteBase, SQLModel):
    uuid: Optional[uuid_pkg.UUID]
    hashtags: list["HashtagCreate"] = []
