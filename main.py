from forum_analyzer import analyze_course
from db_connector import Course
import time
import math

start_time = time.time()

courses = [
    {'key': 'course-v1:HarvardX+PH125.8x+2T2018', 'platform': 'Edx'},  # 5 Threads
    {'key': 'course-v1:UCSanDiegoX+DSE200x+1T2019a', 'platform': 'Edx'},  # 180 Threads
    {'key': 'course-v1:Microsoft+DAT236x+1T2019a', 'platform': 'Edx'},  # 99 Threads
    {'key': 'course-v1:CurtinX+IOT3x+2T2019', 'platform': 'Edx'},  # 15 threads
    {'key': 'course-v1:MITx+6.002.3x+2T2019', 'platform': 'Edx'},  # 7 threads
    {'key': 'course-v1:DelftXRWTHx+BioBased1x+2T2019', 'platform': 'Edx'},  # 38 threads
]

courses_1 = list(Course.get_courses({}, {'key': 1, 'platform': 1}))
#  Get Courses
# print('Use Actual Dataset (y/n)?')
while True:
    print('Enter Limit to Process (Full Dataset Size =', courses_1.__len__(), ')')
    limit = input()
    limit = int(limit)
    if courses_1.__len__() >= limit > 0:
        break
    else:
        print('Limit is Invalid, Please re-enter')

if limit > courses.__len__():
    courses.extend(courses_1[0:(limit - courses.__len__())])
elif limit < courses.__len__():
    courses = courses[0:limit]

print('Selected Dataset Size:', courses.__len__())

# if dataset == 'y':

''' ANALYZE DATA - Will save rating to database'''
for course in courses:
    analyze_course(course)

''' NORMALIZE DATA '''


# Performing Normalization on the 2 Scores
def normalize(courses_alt):
    # Get Processed Courses
    # courses = Course.get_courses(
    #     {'$and': [{'forum_activity_rating': {'$exists': 1}}, {'course_rating': {'$exists': 1}}]})
    # courses = list(courses)
    print('BEFORE Normalization')
    for course in courses_alt:
        print('Course Rating:\t', course['course_rating'], 'Forum Activity Rating:\t',
              course['forum_activity_rating'], 'Course:', course['key'])
    # for course in courses_alt:
    #     if 'forum_activity_rating' in course.keys() and 'course_rating' in course.keys():
    #         courses.append(course)

    print('Filtered Courses:', courses.__len__())
    e_value = 2.718

    for course in courses_alt:
        # course['course_rating'] = math.log(course['course_rating'], e_value)
        # course['forum_activity_rating'] = math.log(course['forum_activity_rating'], e_value)
        # course['course_rating'] = math.sqrt(course['course_rating'])
        # course['forum_activity_rating'] = math.sqrt(course['forum_activity_rating'])
        course['course_rating'] = course['course_rating'] ** (1. / 6.)
        course['forum_activity_rating'] = course['forum_activity_rating'] ** (1. / 6.)

    # FOR = Forum Activity Rating
    max_rating = 0
    for course in courses_alt:
        if course['forum_activity_rating'] > max_rating:
            max_rating = course['forum_activity_rating']

    for course in courses_alt:
        rating = (course['forum_activity_rating'] / max_rating) * 5
        course['forum_activity_rating'] = round(rating, 2)

    # for x in range(1):
    #     print(courses[x]['forum_activity_rating'])

    # FOR = Course Rating
    max_rating = 0
    for course in courses_alt:
        if course['course_rating'] > max_rating:
            max_rating = course['course_rating']

    for course in courses_alt:
        rating = (course['course_rating'] / max_rating) * 5
        course['course_rating'] = round(rating, 2)

    # for x in range(1):
    #     print(courses[x]['course_rating'])
    print('----- Normalization Complete -----')
    print('Dataset Size:', courses.__len__())

    return courses_alt


# Course.get_courses({'$and': [{'forum_activity_rating': $exists{'': 1}}, {'rating': {'$exists': 1}}, {'course_rating': {'$exists': 1}}]})
print('--- Beginning Normalization ---')
course_keys = []
for course in courses:
    course_keys.append(course['key'])
courses = list(Course.get_courses({'key': {'$in': course_keys}}, None))
# print(courses[0])
courses_alt = normalize(courses)
print('AFTER Normalization')
for course in courses_alt:
    print('Course Rating:\t', course['course_rating'], 'Forum Activity Rating:\t',
          course['forum_activity_rating'], 'Course:', course['key'])
end_time = time.time()
elapsed_time = end_time - start_time
print('Elapsed Time:', elapsed_time)
