from .hashtag_models import Hashtag, HashtagRead, HashtagBase, HashtagReadWithNotes, HashtagCreate
from .note_models import Note, NoteBase, NoteRead, NoteReadWithHashtags, NoteHashtagLink, NoteCreate
from .user_models import User, UserBase, UserRead, UserCreate, UserLogin, UserRegister
from .sentiment_models import Sentiment, SentimentAdviceLink, Advice, SentimentReadWithAdvices, SentimentRead


Hashtag.update_forward_refs(Note=Note)
Note.update_forward_refs(Hashtag=Hashtag)
NoteReadWithHashtags.update_forward_refs(HashtagRead=HashtagRead)
HashtagReadWithNotes.update_forward_refs(NoteRead=NoteRead)
NoteCreate.update_forward_refs(HashtagCreate=HashtagCreate)
Advice.update_forward_refs(Sentiment=Sentiment)
NoteRead.update_forward_refs(HashtagRead=HashtagRead)


__all__ = [
    "Hashtag",
    "HashtagBase",
    "HashtagRead",
    "HashtagReadWithNotes",
    "HashtagCreate",
    "Note",
    "NoteBase",
    "NoteCreate",
    "NoteHashtagLink",
    "NoteRead",
    "NoteReadWithHashtags",
    "User",
    "UserBase",
    "UserCreate",
    "UserRead",
]
