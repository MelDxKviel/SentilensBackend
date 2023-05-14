import uuid as uuid_pkg
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.auth import AuthHandler
from app.database import get_session
from app.models import Note, NoteRead, NoteReadWithHashtags, NoteCreate, Hashtag, NoteHashtagLink, Sentiment, \
    SentimentReadWithAdvices
from app.models.sentiment_models import Text
from app.utils import analyze_sentiment, get_sentiment

note_router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
    responses={404: {"description": "Not found"}},
)
auth_handler = AuthHandler()


@note_router.get("/", response_model=list[NoteReadWithHashtags])
async def get_notes(session: Session = Depends(get_session),
                    hashtag_title: str = None,
                    user_id=Depends(auth_handler.auth_wrapper)):
    if hashtag_title:
        notes = session.exec(
            select(Note).where(Note.owner_id == user_id).where(Note.hashtags.any(Hashtag.title == hashtag_title))
        ).all()
    else:
        notes = session.exec(
            select(Note).where(Note.owner_id == user_id).order_by(Note.created_at)
        ).all()
    return notes


@note_router.get("/{note_id}", response_model=NoteReadWithHashtags)
async def get_note(note_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                   user_id=Depends(auth_handler.auth_wrapper)):
    note = session.exec(
        select(Note).where(Note.uuid == note_id).where(Note.owner_id == user_id)
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@note_router.post("/{note_id}/add_hashtag", response_model=NoteReadWithHashtags)
async def add_note_hashtag(note_id: uuid_pkg.UUID, hashtag_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                           user_id=Depends(auth_handler.auth_wrapper)):
    note = session.exec(
        select(Note).where(Note.uuid == note_id).where(Note.owner_id == user_id)
    ).first()
    hashtag = session.exec(
        select(Hashtag).where(Hashtag.uuid == hashtag_id).where(Hashtag.owner_id == user_id)
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    links = session.exec(
        select(NoteHashtagLink)
    ).all()
    if any(link.note_uuid == note_id and link.hashtag_uuid for link in links):
        raise HTTPException(status_code=418, detail="Hashtag already assigned")
    note_hashtag_link = NoteHashtagLink(note_id=note.uuid, hashtag_id=hashtag.uuid)
    session.add(note_hashtag_link)
    session.commit()
    session.refresh(note)
    return NoteReadWithHashtags.from_orm(note)


@note_router.post("/", response_model=NoteReadWithHashtags)
async def create_note(note: NoteCreate, session: Session = Depends(get_session),
                      user_id=Depends(auth_handler.auth_wrapper)):
    existing_hashtags = session.exec(
        select(Hashtag).where(Hashtag.owner_id == user_id).order_by(Hashtag.title)
    ).all()
    hashtags_ids = []
    hashtags_for_create = []

    for hashtag in note.hashtags:
        if (ht := session.exec(
                select(Hashtag).where(Hashtag.title == hashtag.title).where(Hashtag.owner_id == user_id)
        ).first()) in existing_hashtags:
            hashtags_ids.append(ht.uuid)
        else:
            new_hashtag = Hashtag(title=hashtag.title, owner_id=user_id)
            hashtags_for_create.append(new_hashtag)

    for hashtag in hashtags_for_create:
        session.add(hashtag)
        session.commit()
        session.refresh(hashtag)
        hashtags_ids.append(hashtag.uuid)

    db_note = Note.from_orm(note)
    db_note.sentiment_id = get_sentiment(db_note.content)
    db_note.mood_value = analyze_sentiment(db_note.content)
    db_note.owner_id = user_id

    session.add(db_note)
    session.commit()

    for hashtag_id in hashtags_ids:
        note_hashtag_link = NoteHashtagLink(note_uuid=db_note.uuid, hashtag_uuid=hashtag_id)
        session.add(note_hashtag_link)
        session.commit()

    return db_note


@note_router.delete("/{note_id}")
async def delete_note(note_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                      user_id=Depends(auth_handler.auth_wrapper)):
    note = session.exec(
        select(Note).where(Note.uuid == note_id).where(Note.owner_id == user_id)
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return {"message": "Note deleted"}


@note_router.put("/{note_id}", response_model=NoteRead)
async def update_note(note_id: uuid_pkg.UUID, note: NoteCreate, session: Session = Depends(get_session),
                      user_id=Depends(auth_handler.auth_wrapper)):
    db_note = session.exec(
        select(Note).where(Note.uuid == note_id).where(Note.owner_id == user_id)
    ).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db_note.title = note.title
    db_note.content = note.content
    db_note.mood_value = analyze_sentiment(note.content)
    db_note.sentiment_id = get_sentiment(db_note.content)
    db_note.updated_at = datetime.now()

    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@note_router.patch("/{note_id}", response_model=NoteRead)
async def update_note_partial(note_id: uuid_pkg.UUID, note: NoteCreate, session: Session = Depends(get_session),
                              user_id=Depends(auth_handler.auth_wrapper)):
    db_note = session.exec(
        select(Note).where(Note.uuid == note_id).where(Note.owner_id == user_id)
    ).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.title:
        db_note.title = note.title
    if note.content:
        db_note.content = note.content
        db_note.mood_value = analyze_sentiment(note.content)
        db_note.sentiment_id = get_sentiment(db_note.content)
    db_note.updated_at = datetime.now()
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@note_router.get("/{note_id}/analyze", response_model=SentimentReadWithAdvices)
async def analyze_sentiment_by_note(note_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                                    user_id=Depends(auth_handler.auth_wrapper)):
    db_note = session.exec(
        select(Note).where(Note.uuid == note_id).where(Note.owner_id == user_id)
    ).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db_sentiment = session.exec(
        select(Sentiment).where(Sentiment.title == db_note.sentiment_id)
    ).first()
    return SentimentReadWithAdvices.from_orm(db_sentiment)


@note_router.post("/analyze-by-text", response_model=SentimentReadWithAdvices)
async def analyze_sentiment_by_text(text: Text, session: Session = Depends(get_session)):
    mood = get_sentiment(text.text)
    db_sentiment = session.exec(
        select(Sentiment).where(Sentiment.title == mood)
    ).first()
    return SentimentReadWithAdvices.from_orm(db_sentiment)
