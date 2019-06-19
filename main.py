from nlp_processor import analyze_sentiment
from db_connector import Thread, Course
from datetime import datetime
import statistics
from pprint import pprint

id_1 = 'course-v1:Microsoft+DAT236x+1T2019a'
course_key = 'course-v1:UCSanDiegoX+DSE200x+1T2019a'

results = Thread.get_discussion_threads_with_responses(course_key)
print('Retrieved 100 Threads from the Database')


def get_thread_body_data(raw_thread):
    thread_data = []
    try:
        thread_data.append(raw_thread['body'])
        if 'children' in raw_thread.keys():
            for child in raw_thread['children']:
                thread_data.extend(get_thread_body_data(child))
        if 'non_endorsed_responses' in raw_thread.keys():
            for child in raw_thread['non_endorsed_responses']:
                thread_data.extend(get_thread_body_data(child))
    except:
        print('Error Occurred')
        pass
    return thread_data


print('Analyzing Sentiments')
sentiment_data = []
count = 1
for thread in results:
    print('Progress:', count, '%')
    body_data = get_thread_body_data(thread)
    body_sentiment_values = []
    for body in body_data:
        body_sentiment = analyze_sentiment(body)
        body_sentiment_values.append(body_sentiment.score)
    average_sentiment_value = statistics.mean(body_sentiment_values)
    sentiment_data.append(
        {'id': thread['id'], 'is_sentiment_analyzed': True, 'sentiment_score': average_sentiment_value})
    count += 1
    break

print('Sentiments Analyzed (Thread Count=', sentiment_data.__len__(), ')')
print('Inserting Sentiment Data into Database')
result = Thread.upsert_threads(sentiment_data)
if result:
    print('Sentiment Scores have been saved to the database')

print('Calculating Overall Course Sentiment Score')
sentiment_values_of_each_thread = []
for info in sentiment_data:
    try:
        sentiment_values_of_each_thread.append(info['sentiment_score'])
    except:
        print('Error Occurred: Retrieving sentiment_score from sentiment_info')
        print(info)
        pass

average_sentiment_score = statistics.mean(sentiment_values_of_each_thread)
course = Course.get_course(course_key)

course['sentiment_score'] = average_sentiment_score
course['sentiment_analyzed_date_time'] = datetime.now()

Course.upsert_courses([course])

print('Course Sentiment Information Stored in Database (Threads Analyzed = {})'.format(count - 1))
