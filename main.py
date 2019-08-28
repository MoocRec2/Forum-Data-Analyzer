from forum_analyzer import analyze_course

courses = [
    'course-v1:HarvardX+PH125.8x+2T2018',  # 5 Threads
    'course-v1:UCSanDiegoX+DSE200x+1T2019a',  # 180 Threads
    'course-v1:Microsoft+DAT236x+1T2019a',  # 99 Threads
    'course-v1:CurtinX+IOT3x+2T2019',  # 15 threads
    'course-v1:MITx+6.002.3x+2T2019',  # 7 threads
    'course-v1:DelftXRWTHx+BioBased1x+2T2019'  # 38 threads
]

for course in courses:
    analyze_course(course)

# analyze_course(course_two)
