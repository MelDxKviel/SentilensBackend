from typing import Optional
import uuid as uuid_pkg
from sqlmodel import SQLModel, Field, Relationship

from .note_models import NoteHashtagLink, Note


class HashtagBase(SQLModel):
    title: str


class Hashtag(HashtagBase, table=True):
    uuid: Optional[uuid_pkg.UUID] = Field(default_factory=uuid_pkg.uuid4, primary_key=True, index=True, nullable=False)
    owner_id: int = Field(default=None, foreign_key="user.id")
    notes: list["Note"] = Relationship(back_populates="hashtags", link_model=NoteHashtagLink)


class HashtagRead(HashtagBase):
    uuid: uuid_pkg.UUID


class HashtagReadWithNotes(HashtagRead):
    notes: list["NoteRead"] = []


class HashtagCreate(HashtagBase):
    pass
