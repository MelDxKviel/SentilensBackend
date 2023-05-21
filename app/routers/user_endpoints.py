from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

from app.database import get_session
from app.auth.auth import AuthHandler, Token
from app.models import User, UserRead, UserLogin, UserRegister, Note

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

    example_note = Note(owner_id=db_user.id, content='''Мы рады приветствовать вас в нашем уютном и интуитивно понятном приложении, где вы сможете сохранять свои мысли, идеи и важные моменты вашей жизни.

Наше приложение предлагает вам не только удобное место для записей, но и уникальную возможность анализировать эмоциональную окраску ваших заметок. Оно распознает эмоции, выраженные в тексте, и помогает вам осознать свои эмоциональные состояния и настроение.

Кроме того, мы предоставляем вам возможность добавлять теги к вашим заметкам, чтобы легко организовывать и находить нужную информацию. Вы можете создавать персональные теги, связывать заметки по темам или проектам, делать поиск по тегам и многое другое.

Мы уверены, что наше приложение поможет вам структурировать ваши мысли, получить больше понимания своих эмоций и быть более организованными в повседневной жизни. Не стесняйтесь делиться своими заметками, и вы обнаружите, что ваше путешествие к саморазвитию и эмоциональному благополучию станет еще более интересным и осознанным.

Спасибо, что выбрали наше приложение! Мы желаем вам вдохновения, продуктивности и гармонии в каждой заметке, которую вы создаете.''',
                        title="Добро пожаловать!")
    session.add(example_note)
    session.commit()
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
