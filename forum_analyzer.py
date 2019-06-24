from nlp_processor import GoogleNLP, VADER
from db_connector import Thread, Course
from datetime import datetime
import statistics
from pprint import pprint


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def analyze_course(course_key):
    print('Beginning to Analyze Course:', course_key)
    results = Thread.get_discussion_threads_with_responses(course_key)
    print('Retrieved Threads from the Database')

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
    iteration = 1
    total_thread_count = results.count()
    post_count = 0
    for thread in results:
        print('Progress:', (iteration / total_thread_count) * 100, '%')
        body_data = get_thread_body_data(thread)
        body_sentiment_values = []
        for body in body_data:
            post_count += 1
            body_sentiment = VADER.analyze_sentiment(body)
            body_sentiment_values.append(body_sentiment['score'])
        average_sentiment_value = statistics.mean(body_sentiment_values)
        sentiment_data.append(
            {'id': thread['id'], 'is_sentiment_analyzed': True, 'sentiment_score': average_sentiment_value})
        iteration += 1

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
    weighted_sentiment_score = average_sentiment_score * total_thread_count

    course = Course.get_course(course_key)
    latest_thread = Thread.get_latest_thread_of_course(course_key)
    earliest_thread = Thread.get_earliest_thread_of_course(course_key)
    min_date = datetime.strptime(earliest_thread['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    max_date = datetime.strptime(latest_thread['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    months = diff_month(max_date, min_date)
    if months == 0:
        months = 1
    thread_count = Thread.get_thread_count_of_course(course_key)
    threads_per_month = thread_count / months
    last_activity_date = Thread.get_last_activity_date(course_key)
    print(months)
    try:
        course['score'] = weighted_sentiment_score
    except:
        print('Exception Thrown line 82: weighted_sentiment_score=', weighted_sentiment_score)
        pprint(course)

    try:
        course['statistics'] = {
            'threads_per_month': threads_per_month,
            'last_active_date': last_activity_date['last_activity_at'],
            'total_thread_count': thread_count,
            'total_post_count': post_count
        }
    except:
        print({
            'threads_per_month': threads_per_month,
            'last_active_date': last_activity_date['last_activity_at'],
            'total_thread_count': thread_count,
            'total_post_count': post_count
        })
    course['analyzed_date_time'] = datetime.now()

    Course.upsert_courses([course])

    print('Course Sentiment Information Stored in Database (Threads Analyzed = {})'.format(iteration - 1))

    print('Course Statistics = ', course['statistics'])
