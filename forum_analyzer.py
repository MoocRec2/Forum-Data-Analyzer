from nlp_processor import GoogleNLP, VADER
from db_connector import Thread, Course
from datetime import datetime
import statistics
from pprint import pprint


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


# Gets all the nested posts into an array
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


def calculate_forum_activity_rating():
    return 0


def calculate_course_rating():
    return 0


# The parent method of the program
def analyze_course(course_key):
    print('Beginning to Analyze Course:', course_key)
    results = Thread.get_discussion_threads_with_responses(course_key)
    print('Retrieved Threads from the Database (Threads with Responses)')

    total_threads_with_responses_count = results.count()
    print('No. of Threads with Responses:', total_threads_with_responses_count)

    print('Analyzing Sentiments')
    sentiment_data = []
    posts_per_thread_count = []
    post_count = 0
    iteration = 0
    for thread in results:
        body_data = get_thread_body_data(thread)
        posts_per_thread_count.append(body_data.__len__())
        body_sentiment_values = []
        users = []
        for body in body_data:
            post_count += 1
            body_sentiment = VADER.analyze_sentiment(body)
            body_sentiment_values.append(body_sentiment['score'])
            username_missing_count = 0
            try:
                if thread['username'] not in users:
                    users.append(thread['username'])
            except KeyError:
                username_missing_count += 1
            # print('Username Missing Count:', username_missing_count)
        average_sentiment_value = statistics.mean(body_sentiment_values)
        sentiment_data.append(
            {
                'id': thread['id'],
                'is_sentiment_analyzed': True,
                'sentiment_score': average_sentiment_value,
                'unique_user_count': users.__len__()
            }
        )
        iteration += 1

    print('--- Posts Statistics ---')
    print('Average Posts per Thread:', statistics.mean(posts_per_thread_count))
    print('Maximum Posts per Thread:', max(posts_per_thread_count))
    print('Minimum Posts per Thread:', min(posts_per_thread_count))

    # print('Thread Count =', iteration, 'and total_thread_count=', total_threads_with_responses_count)

    print('Sentiments Analyzed (Thread Count=', sentiment_data.__len__(), ')')
    print('Inserting Sentiment Data into Database')
    result = Thread.upsert_threads(sentiment_data)  # Might be unnecessary because processing is fast enough

    if result:
        print('Intermediate Sentiment Scores have been saved to the database')

    # print('Calculating Overall Course Sentiment Score')
    # print('Course Rating: Beginning Processing')
    print('Continuing Processing')
    sentiment_values_of_each_thread = []
    for info in sentiment_data:
        try:
            sentiment_values_of_each_thread.append(info['sentiment_score'])
        except:
            print('Error Occurred: Retrieving sentiment_score from sentiment_info')
            print(info)
            pass

    average_sentiment_score = statistics.mean(sentiment_values_of_each_thread)

    # Addition of the sentiment scores of the individual posts
    weighted_sentiment_score = average_sentiment_score * total_threads_with_responses_count
    print('--- Ratings ---')
    print('Course Rating:', weighted_sentiment_score)

    forum_activity_rating = 0

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

    last_active_date = datetime.strptime(last_activity_date['last_activity_at'], "%Y-%m-%dT%H:%M:%SZ")
    today = datetime.today()

    delta = today - last_active_date
    # score = weighted_sentiment_score * ((months * 30) - delta.days)
    score = weighted_sentiment_score * ((months * 30))

    print('Forum Activity Rating:', score)

    try:
        course['score'] = weighted_sentiment_score
        course['course_rating'] = weighted_sentiment_score
        course['forum_activity_rating'] = forum_activity_rating
    except:
        print('Exception Thrown line 82: weighted_sentiment_score=', weighted_sentiment_score)
        pprint(course)

    try:
        course['statistics'] = {
            'threads_per_month': threads_per_month,
            'last_active_date': last_activity_date['last_activity_at'],
            'total_thread_count': thread_count,
            'responded_thread_count': total_threads_with_responses_count,
            'total_post_count': post_count
        }
    except:
        print({
            'threads_per_month': threads_per_month,
            'last_active_date': last_activity_date['last_activity_at'],
            'total_thread_count': thread_count,
            'responded_thread_count': total_threads_with_responses_count,
            'total_post_count': post_count
        })
    course['analyzed_date_time'] = datetime.now()

    Course.upsert_courses([course])

    print('Course Sentiment Information Stored in Database (Threads Analyzed = {})'.format(iteration - 1))
    course['statistics']['sentiment_score'] = average_sentiment_score
    print('Course Statistics = ', course['statistics'])
