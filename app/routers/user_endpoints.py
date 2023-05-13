from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

from app.database import get_session
from app.auth.auth import AuthHandler, Token
from app.models import User, UserRead, UserLogin, UserRegister

user_router = APIRouter(
    prefix="/user",
    tags=["Users"],
    responses={404: {"description": "Not found"},
               },
)
auth_handler = AuthHandler()


@user_router.post("/register", response_model=UserRead, status_code=201, responses={
    400: {"description": "Email or username already registered"},
    201: {"description": "User created successfully"}})
async def register_user(user: UserRegister, session: Session = Depends(get_session)):
    result = session.exec(
        select(User)
    ).all()
    if any(u.email == user.email for u in result):
        raise HTTPException(status_code=400, detail="Email already registered")
    if any(u.username == user.username for u in result):
        raise HTTPException(status_code=400, detail="Username already registered")
    user.password = auth_handler.get_password_hash(user.password)
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserRead.from_orm(db_user)


@user_router.post("/login", response_model=Token)
async def login_user(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not auth_handler.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth_handler.encode_token(db_user.id)
    return access_token
