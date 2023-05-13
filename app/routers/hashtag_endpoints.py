from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
import uuid as uuid_pkg

from app.models import Hashtag, HashtagRead, HashtagReadWithNotes, HashtagCreate
from app.database import get_session
from app.auth import AuthHandler

hashtag_router = APIRouter(
    prefix="/hashtags",
    tags=["Hashtags"],
    responses={404: {"description": "Not found"}},
)

auth_handler = AuthHandler()


@hashtag_router.get("/", response_model=list[HashtagRead])
async def get_hashtags(session: Session = Depends(get_session),
                       user_id=Depends(auth_handler.auth_wrapper)):
    hashtags = session.exec(
        select(Hashtag).where(Hashtag.owner_uuid == user_id).order_by(Hashtag.title)
    ).all()
    return hashtags


@hashtag_router.get("/{hashtag_id}", response_model=HashtagReadWithNotes)
async def get_hashtag(hashtag_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                      user_id=Depends(auth_handler.auth_wrapper)):
    hashtag = session.exec(
        select(Hashtag).where(Hashtag.uuid == hashtag_id).where(Hashtag.owner_uuid == user_id)
    )
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    return hashtag


@hashtag_router.post("/", response_model=HashtagRead)
async def create_hashtag(hashtag: HashtagCreate, session: Session = Depends(get_session),
                         user_id=Depends(auth_handler.auth_wrapper)):
    new_hashtag = Hashtag(title=hashtag.title, owner_id=user_id)
    session.add(new_hashtag)
    session.commit()
    session.refresh(new_hashtag)
    return new_hashtag


@hashtag_router.delete("/{hashtag_id}", response_model=HashtagRead)
async def delete_hashtag(hashtag_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                         user_id=Depends(auth_handler.auth_wrapper)):
    hashtag = session.exec(
        select(Hashtag).where(Hashtag.uuid == hashtag_id).where(Hashtag.owner_uuid == user_id)
    ).first()
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    session.delete(hashtag)
    session.commit()
    return hashtag


@hashtag_router.put("/{hashtag_id}", response_model=HashtagRead)
async def update_hashtag(hashtag_id: uuid_pkg.UUID, hashtag: HashtagCreate, session: Session = Depends(get_session),
                         user_id=Depends(auth_handler.auth_wrapper)):
    db_hashtag = session.exec(
        select(Hashtag).where(Hashtag.uuid == hashtag_id).where(Hashtag.owner_uuid == user_id)
    ).first()
    if not db_hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    db_hashtag.title = hashtag.title
    session.add(db_hashtag)
    session.commit()
    return db_hashtag
