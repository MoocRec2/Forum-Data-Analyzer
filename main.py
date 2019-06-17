from sentiment_analyzer import analyze_sentiment
from db_connector import Thread
from pprint import pprint

# analyze_sentiment('You are dying')

id_1 = 'course-v1:Microsoft+DAT236x+1T2019a'
has_data = 'course-v1:UCSanDiegoX+DSE200x+1T2019a'

results = Thread.get_discussion_threads_with_responses(has_data)


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


data = []
for thread in results:
    body_data = get_thread_body_data(thread)
    data.append({'title': thread['title'], 'body_data': body_data})

print(data.__len__())

# text_data = get_thread_body_data(results[0])

# print(results[0]['title'])
# print(text_data)
#
# for data in result:
#     # print(data)
#     value = analyze_sentiment(data['body'])
#     print(value.score)
#     print('qwqewqwe')
#     # print(''.format(value))
#     break
