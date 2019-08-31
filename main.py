from forum_analyzer import analyze_course
from db_connector import Course
import time

start_time = time.time()

courses = [
    {'key': 'course-v1:HarvardX+PH125.8x+2T2018', 'platform': 'Edx'},  # 5 Threads
    {'key': 'course-v1:UCSanDiegoX+DSE200x+1T2019a', 'platform': 'Edx'},  # 180 Threads
    {'key': 'course-v1:Microsoft+DAT236x+1T2019a', 'platform': 'Edx'},  # 99 Threads
    {'key': 'course-v1:CurtinX+IOT3x+2T2019', 'platform': 'Edx'},  # 15 threads
    {'key': 'course-v1:MITx+6.002.3x+2T2019', 'platform': 'Edx'},  # 7 threads
    {'key': 'course-v1:DelftXRWTHx+BioBased1x+2T2019', 'platform': 'Edx'},  # 38 threads
]

#  Get Courses
print('Use Actual Dataset (y/n)?')
dataset = input()
if dataset == 'y':
    courses = list(Course.get_courses({}))

''' ANALYZE DATA - Will save rating to database'''
for course in courses:
    analyze_course(course)

''' NORMALIZE DATA '''


# Performing Normalization on the 2 Scores
def normalize(courses_alt):
    # Get Processed Courses
    courses = Course.get_courses(
        {'$and': [{'forum_activity_rating': {'$exists': 1}}, {'course_rating': {'$exists': 1}}]})
    courses = list(courses)
    # for course in courses_alt:
    #     if 'forum_activity_rating' in course.keys() and 'course_rating' in course.keys():
    #         courses.append(course)

    print('Filtered Courses:', courses.__len__())

    # FOR = Forum Activity Rating
    max_rating = 0
    for course in courses:
        if course['forum_activity_rating'] > max_rating:
            max_rating = course['forum_activity_rating']

    for course in courses:
        rating = (course['forum_activity_rating'] / max_rating) * 5
        course['forum_activity_rating'] = rating

    # for x in range(1):
    #     print(courses[x]['forum_activity_rating'])

    # FOR = Course Rating
    max_rating = 0
    for course in courses:
        if course['course_rating'] > max_rating:
            max_rating = course['course_rating']

    for course in courses:
        rating = (course['course_rating'] / max_rating) * 5
        course['course_rating'] = rating

    # for x in range(1):
    #     print(courses[x]['course_rating'])
    print('----- Normalization Complete -----')
    print('Dataset Size:', courses.__len__())


# Course.get_courses({'$and': [{'forum_activity_rating': {'$exists': 1}}, {'rating': {'$exists': 1}}, {'course_rating': {'$exists': 1}}]})
print('--- Beginning Normalization ---')
normalize(courses)
end_time = time.time()
elapsed_time = end_time - start_time
print('Elapsed Time:', elapsed_time)
