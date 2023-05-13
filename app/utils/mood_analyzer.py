from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googletrans import Translator
from app.models import Note


def analyze_sentiment(text):
    translator = Translator()
    translated_text = translator.translate(text).text
    sid = SentimentIntensityAnalyzer()
    return sid.polarity_scores(translated_text)['compound']


def get_sentiment(text: str):
    mood_value = analyze_sentiment(text)

    if mood_value > 0:
        sentiment = 'Позитивное'
    elif mood_value < 0:
        sentiment = 'Негативное'
    else:
        sentiment = 'Нейтральное'

    return sentiment
