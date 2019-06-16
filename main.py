from sentiment_analyzer import analyze_sentiment
from db_connector import Thread
from pprint import pprint

# analyze_sentiment('You are dying')

id_1 = 'course-v1:Microsoft+DAT236x+1T2019a'
has_data = 'course-v1:UCSanDiegoX+DSE200x+1T2019a'

results = Thread.get_discussion_threads_with_responses(has_data)

for result in results:
    for child in result['children']:
        pprint(child)
    break
