from nltk.sentiment.vader import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator


def analyze_sentiment(text):
    translated_text = GoogleTranslator(source='auto', target='en').translate(text)
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
