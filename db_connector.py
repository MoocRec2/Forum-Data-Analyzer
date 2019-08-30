from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import json

platform_to_collection_mapping = {
    'Edx': 'threads',
    'FutureLearn': 'future_learn_threads',
    'Coursera': 'coursera_threads'
}

with open('./db_credentials.json', 'r') as f:
    db_credentials = json.load(f)

connection_string = db_credentials['connectionString']

# client = MongoClient('mongodb://api:backendapi1@ds157901.mlab.com:57901/moocrecv2?retryWrites=false')
# client = MongoClient('mongodb://localhost:27017/moocrecv2')
client = MongoClient(connection_string)

database = client.moocrecv2


class Thread:

    @staticmethod
    def save_threads(threads):
        try:
            result = database.threads.insert(threads)
            return result
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
        except:
            print('An Error Occurred')

    @staticmethod
    def upsert_threads(threads):
        try:
            for thread in threads:
                database.threads.update_one({'id': thread['id']}, {"$set": thread}, upsert=True)
            return True
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
            return False
        except:
            print('An Error Occurred')
            return False

    @staticmethod
    def get_discussion_threads(search_query, platform):
        try:
            results = database[platform_to_collection_mapping[platform]].find(search_query)
            return results
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
            return

    @staticmethod
    def get_discussion_threads_with_responses(course_id):
        try:
            results = database.threads.find(
                {
                    'course_id': course_id,
                    'thread_type': 'discussion',
                    '$or': [
                        {'children': {'$exists': 'true'}},
                        {'non_endorsed_responses': {'$exists': 'true'}}
                    ]
                }
            )
            return results
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
            return

    @staticmethod
    def get_latest_thread_of_course(course_id):
        try:
            result = database.threads.find({'course_id': course_id}).sort('created_at', -1).limit(1)
            return result[0]
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
        except:
            print('An Error Occurred')

    @staticmethod
    def get_earliest_thread_of_course(course_id):
        try:
            result = database.threads.find({'course_id': course_id}).sort('created_at', 1).limit(1)
            return result[0]
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
        except:
            print('An Error Occurred')

    @staticmethod
    def get_discussion_thread_count_of_course(course_id):
        try:
            count = database.threads.count_documents({'course_id': course_id, 'thread_type': 'discussion'})
            return count
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
        except:
            print('An Error Occurred')

    @staticmethod
    def get_discussion_threads_of_course(course_id):
        try:
            documents = database.threads.find({'course_id': course_id, 'thread_type': 'discussion'})
            return documents
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
        except:
            print('An Error Occurred')

    @staticmethod
    def get_question_thread_count_of_course(course_id):
        try:
            count = database.threads.count_documents({'course_id': course_id, 'thread_type': 'question'})
            return count
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
        except:
            print('An Error Occurred')

    @staticmethod
    def get_question_threads_of_course(course_id):
        try:
            documents = database.threads.find({'course_id': course_id, 'thread_type': 'question'})
            return documents
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
        except:
            print('An Error Occurred')

    @staticmethod
    def get_thread_count_of_course(course_id):
        try:
            result = database.threads.count_documents({'course_id': course_id})
            return result
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
        except:
            print('An Error Occurred')

    @staticmethod
    def get_sentiment_analyzed_threads():
        try:
            results = database.Threads.find({
                'course_id': 'course-v1:UCSanDiegoX+DSE200x+1T2019a',
                'thread_type': 'discussion',
                '$or': [
                    {'children': {'$exists': 'true'}},
                    {'non_endorsed_responses': {'$exists': 'true'}}
                ],
                '$and': [{'is_sentiment_analyzed': {'$exists': 'true'}}, {'sentiment_score': {'$exists': 'true'}}]
            }, {'is_sentiment_analyzed': 1, 'sentiment_score': 1}).sort({'sentiment_score': -1})
            return results
        except:
            return []

    @staticmethod
    def get_last_activity_date(course_id):
        try:
            result = database.threads.find({'course_id': course_id}).sort('last_activity_at', -1).limit(1)
            return result[0]
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
        except:
            print('An Error Occurred')


class Course:

    @staticmethod
    def upsert_courses(courses):
        try:
            for course in courses:
                database.courses.update_one({'key': course['key']}, {"$set": course}, upsert=True)
            return True
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
            return False
        except:
            print('An Error Occurred')
            return False

    @staticmethod
    def get_course(search_query):
        try:
            courses = database.courses.find(search_query)
            return courses[0]
        except:
            return None
            pass

    @staticmethod
    def get_courses(search_query):
        try:
            courses = database.courses.find(search_query)
            return courses
        except:
            return None
            pass
