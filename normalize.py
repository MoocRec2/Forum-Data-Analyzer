from forum_analyzer import analyze_course
from nlp_processor import GoogleNLP, VADER
from db_connector import Thread, Course
from datetime import datetime
import statistics
from pprint import pprint
from random import randrange, random

# # TODO: Retrieve Courses
# courses_with_forum_ratings = list(Course.get_courses({'forum_activity_rating': {'$exists': 1}}))
#
# print('Count:', courses_with_forum_ratings.__len__())


courses = list(Course.get_courses({}))
print('Count:', courses.__len__())

list = []

# for x in range(10):
#     value = randrange(1000, 5000) / 1000
#     # if value == 5:
#     #     value -= 0.5
#     # elif value == 1:
#     #     value +=
#     print(value)
print('Processing')
for course in courses:
    rating_1 = randrange(1000, 5000) / 1000
    rating_2 = randrange(1000, 5000) / 1000
    course['course_rating'] = rating_1
    course['forum_activity_rating'] = rating_2

print('Processed')
status = Course.upsert_courses(courses)
print(status)
