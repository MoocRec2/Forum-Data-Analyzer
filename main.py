from sentiment_analyzer import analyze_sentiment
from db_connector import Thread
from pprint import pprint

# analyze_sentiment('You are dying')

id_1 = 'course-v1:Microsoft+DAT236x+1T2019a'
has_data = 'course-v1:UCSanDiegoX+DSE200x+1T2019a'

results = Thread.get_discussion_threads_with_responses(has_data)

thread_text = ['qwe']


def get_text_data(thread):
    data = []
    try:
        data.append(thread['body'])
        if 'children' in thread.keys():
            for child in thread['children']:
                data.extend(get_text_data(child))
        if 'non_endorsed_responses' in thread.keys():
            for child in thread['non_endorsed_responses']:
                data.extend(get_text_data(child))
    except:
        pass
    return data


text_data = get_text_data(results[0])

print(results[0]['title'])
print(text_data)
#
# for data in result:
#     # print(data)
#     value = analyze_sentiment(data['body'])
#     print(value.score)
#     print('qwqewqwe')
#     # print(''.format(value))
#     break
