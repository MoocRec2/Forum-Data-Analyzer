from nlp_processor import GoogleNLP, VADER
from db_connector import Thread, Course
from datetime import datetime
import statistics
from pprint import pprint


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


course_four = 'course-v1:HarvardX+PH125.8x+2T2018'

# latest_thread = Thread.get_latest_thread_of_course(course_four)
# earliest_thread = Thread.get_earliest_thread_of_course(course_four)
#
# print(earliest_thread['created_at'])
# print(latest_thread['created_at'])
#
# min_date = datetime.strptime(earliest_thread['created_at'], "%Y-%m-%dT%H:%M:%SZ")
# max_date = datetime.strptime(latest_thread['created_at'], "%Y-%m-%dT%H:%M:%SZ")
# months = diff_month(max_date, min_date)
# print(months)

# count = Thread.get_thread_count_of_course(course_four)
# print(count)


last_thread = Thread.get_last_activity_date(course_four)
pprint(last_thread['last_activity_at'])
last_active_date = datetime.strptime(last_thread['last_activity_at'], "%Y-%m-%dT%H:%M:%SZ")
today = datetime.today()

delta = today - last_active_date
print(delta.days)
