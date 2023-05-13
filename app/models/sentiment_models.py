from sqlmodel import SQLModel, Relationship, Field
from typing import Optional


class SentimentAdviceLink(SQLModel, table=True):
    advice_title: Optional[str] = Field(default=None, foreign_key="advice.title", primary_key=True)
    sentiment_title: Optional[str] = Field(default=None, foreign_key="sentiment.title", primary_key=True)


class Advice(SQLModel, table=True):
    title: str = Field(primary_key=True)
    description: str = Field(default=None)
    url: str = Field(default=None)
    image_url: str = Field(default=None)

    sentiments: list["Sentiment"] = Relationship(back_populates="advices", link_model=SentimentAdviceLink)


class SentimentBase(SQLModel):
    title: str = Field(primary_key=True)
    smile: str = Field(default=None)
    description: str = Field(default=None)


class Sentiment(SentimentBase, table=True):
    advices: list[Advice] = Relationship(back_populates="sentiments", link_model=SentimentAdviceLink)


class SentimentRead(SentimentBase):
    pass


class SentimentReadWithAdvices(SentimentBase):
    advices: list[Advice] = []
