from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googletrans import Translator


def analyze_sentiment(text):
    while True:
        try:
            translator = Translator()
            translated_text = translator.translate(text).text
            break
        except TypeError:
            pass
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
