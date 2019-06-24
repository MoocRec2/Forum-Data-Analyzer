from google.cloud import language_v1
from google.cloud.language_v1 import enums
import six
from pprint import pprint
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


class GoogleNLP:

    @staticmethod
    def analyze_sentiment(content):
        client = language_v1.LanguageServiceClient()

        # content = 'Your text to analyze, e.g. Hello, world!'

        if isinstance(content, six.binary_type):
            content = content.decode('utf-8')

        type_ = enums.Document.Type.PLAIN_TEXT
        document = {'type': type_, 'content': content}

        response = client.analyze_sentiment(document)
        sentiment = response.document_sentiment
        # pprint(response)
        # print('Score: {}'.format(sentiment.score))
        # print('Magnitude: {}'.format(sentiment.magnitude))
        # print(sentiment)

        return sentiment


class VADER:

    @staticmethod
    def analyze_sentiment(content):
        polarity_scores = analyzer.polarity_scores(content)
        data = {'score': polarity_scores['compound']}
        return data
