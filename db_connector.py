from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

client = MongoClient('mongodb://forum_analyzer:admin123@ds157901.mlab.com:57901/moocrecv2')

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
            ).limit(100)
            return results
        except ServerSelectionTimeoutError:
            print('Error Connecting to Database')
            return
        # except:
        #     print('An Error Occurred')
        #     return False
