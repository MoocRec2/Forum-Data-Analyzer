from forum_analyzer import analyze_course

# Contains a MODERATE amount of data
course_one = 'course-v1:Microsoft+DAT236x+1T2019a'  # 5 Threads

# Contains a LARGE amount of data
course_two = 'course-v1:UCSanDiegoX+DSE200x+1T2019a'  # 180 Threads

course_four = 'course-v1:HarvardX+PH125.8x+2T2018'  # 99 Threads

courses = [
    'course-v1:CurtinX+IOT3x+2T2019',  # 15 threads
    'course-v1:MITx+6.002.3x+2T2019',  # 7 threads
    'course-v1:DelftXRWTHx+BioBased1x+2T2019'  # 38 threads
]

# for course in courses:
#     analyze_course(course)

analyze_course(course_two)
