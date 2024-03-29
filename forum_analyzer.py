from nlp_processor import GoogleNLP, VADER
from db_connector import Thread, Course
from datetime import datetime
import statistics
from pprint import pprint


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


# Gets all the nested posts and replies into an array
# Reason: Linear data formats are easier to process
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


def calculate_course_rating(results, total_threads_with_responses_count):
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

    # print('Thread Count =', iteration, 'and total_thread_count=', total_threads_with_responses_count)

    # result = Thread.upsert_threads(sentiment_data)  # Might be unnecessary because processing is fast enough
    #
    # if not result:
    #     print('Intermediate data could not be saved to the database, check database connection')

    sentiment_values_of_each_thread = []
    for info in sentiment_data:
        try:
            sentiment_values_of_each_thread.append(info['sentiment_score'])
        except:
            print('Error Occurred: Retrieving sentiment_score from sentiment_info')
            print(info)
            pass

    average_sentiment_score = statistics.mean(sentiment_values_of_each_thread)

    # To compensate for varying amounts of threads
    weighted_sentiment_score = average_sentiment_score * total_threads_with_responses_count

    return weighted_sentiment_score, posts_per_thread_count, users.__len__()


def calculate_forum_activity_rating(course_key, posts_per_thread_count, responded_thread_count):
    # Calculating Threads per Month
    latest_thread = Thread.get_latest_thread_of_course(course_key)
    earliest_thread = Thread.get_earliest_thread_of_course(course_key)
    min_date = datetime.strptime(earliest_thread['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    max_date = datetime.strptime(latest_thread['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    months = diff_month(max_date, min_date)
    if months == 0:
        months = 1
    total_thread_count = Thread.get_thread_count_of_course(course_key)
    threads_per_month = total_thread_count / months

    # Getting Last Active Date
    last_activity_date = Thread.get_last_activity_date(course_key)
    last_active_date = datetime.strptime(last_activity_date['last_activity_at'], "%Y-%m-%dT%H:%M:%SZ")

    # Calculating Forum Inactive Days
    today = datetime.today()
    delta = today - last_active_date
    # score = weighted_sentiment_score * ((months * 30) - delta.days)

    question_thread_count = Thread.get_question_thread_count_of_course(course_key)
    discussion_thread_count = Thread.get_discussion_thread_count_of_course(course_key)

    # score = threads_per_month * statistics.mean(posts_per_thread_count) / 10

    numerator = threads_per_month * total_thread_count * sum(posts_per_thread_count)
    # print('DELTA:', delta)
    delta = str(delta)
    delta = delta.split('days')
    delta = int(delta[0])
    denominator = delta * (total_thread_count - responded_thread_count)
    scale_adjustment = [0.01, 0.1, 1, 10, 100]
    score = (numerator / denominator) * scale_adjustment[2]
    # print('TEST SCORE:', score)

    stats_dto = {
        'threads_per_month': threads_per_month,
        'thread_count': total_thread_count,
        'last_activity_date': dict(last_activity_date),
        'question_thread_count': question_thread_count,
        'discussion_thread_count': discussion_thread_count
    }

    return score, stats_dto


# The parent method of the program
def analyze_course(course):
    print('---------- Beginning Analysis ----------\n')
    platform = course['platform']
    print('Platform:', platform)

    if platform == 'Edx':

        course_key = course['key']
        print('Course Key:\t', course_key, '\n')

        platform = ''
        course = Course.get_course({'key': course_key})

        responded_threads_list = list(Thread.get_discussion_threads_with_responses(course_key))

        if responded_threads_list.__len__() == 0:
            print('No Threads Found in Database')
            return

        responded_thread_count = responded_threads_list.__len__()

        course_rating, posts_per_thread_count, user_count = calculate_course_rating(responded_threads_list,
                                                                                    responded_thread_count)
        forum_activity_rating, stats_dto = calculate_forum_activity_rating(course_key, posts_per_thread_count,
                                                                           responded_thread_count)

        # Unpacking the DTO
        threads_per_month = stats_dto['threads_per_month']
        thread_count = stats_dto['thread_count']
        last_activity_date = stats_dto['last_activity_date']
        question_thread_count = stats_dto['question_thread_count']
        discussion_thread_count = stats_dto['discussion_thread_count']

        print('--- Calculated Ratings ---')
        print('Course Rating\t\t:\t', course_rating)
        print('Forum Activity Rating\t:\t', forum_activity_rating, '\n')

        # Saving Updated Information in Database

        course['course_rating'] = course_rating
        course['forum_activity_rating'] = forum_activity_rating

        post_count = sum(posts_per_thread_count)

        course['statistics'] = {
            'threads_per_month': threads_per_month,
            'last_active_date': last_activity_date['last_activity_at'],
            'total_thread_count': thread_count,
            'responded_thread_count': responded_thread_count,
            'total_post_count': post_count
        }

        course['analyzed_date_time'] = datetime.now()

        saved = Course.upsert_courses([course])
        if not saved:
            print('Error: Information not Saved to Database')

        print('----- Statistics -----')
        print('Threads per Month\t:\t', threads_per_month)
        print('Last Active Date\t:\t', last_activity_date['last_activity_at'])
        print('Total Thread Count\t:\t', thread_count)
        print('Responded Thread Count\t:\t', responded_thread_count)
        print('Question Thread Type\t:\t', question_thread_count)
        print('Discussion Thread Type\t:\t', discussion_thread_count)
        # print('No. of Unique Users\t:\t', user_count)
        print('Total Post Count\t:\t', post_count)
        print('Average Posts per Thread:\t', statistics.mean(posts_per_thread_count))
        print('Maximum Posts per Thread:\t', max(posts_per_thread_count))
        print('Minimum Posts per Thread:\t', min(posts_per_thread_count), '\n')

    elif platform == 'Coursera' or platform == 'FutureLearn':
        # Note: In the case of Coursera
        threads = list(Thread.get_discussion_threads({'course_id': course['_id']}, platform))

        if threads.__len__() == 0:
            print('Threads Not Available in the Database')
            return
        else:
            print('Threads are available --------------------------------------++++++')
            for thread in threads:
                pass
            length = threads.__len__()
            course_rating, posts_per_thread_count, user_count = calculate_course_rating(threads, length)
            course_key = course['_id']
            forum_activity_rating, stats_dto = calculate_forum_activity_rating(course_key, posts_per_thread_count, 1)

            course['course_rating'] = course_rating
            course['forum_activity_rating'] = forum_activity_rating

            # saved = Course.upsert_courses([course])
            # if not saved:
            #     print('Error: Information not Saved to Database')

    else:
        print('Error: Invalid Platform')

    print('Course Analysis Complete')
