import pandas as pd
import re

course_schedule_url_template = "https://courses.illinois.edu/schedule/2020/spring/:subject/:number"
gpa_visualization_url_template = "https://waf.cs.illinois.edu/discovery/grade_disparity_between_sections_at_uiuc/?subj=:subject&course=:number"

courseScheduleTerm = "Spring 2020"

df_courseSchedule = pd.read_csv('2020-sp.csv')
df_courseSchedule["Number"] = df_courseSchedule["Number"].astype(str)
df_courseSchedule["Course"] = df_courseSchedule["Subject"] + " " + df_courseSchedule["Number"]

df_gpa = pd.read_csv('gpa-dataset.csv')
df_gpa = df_gpa[ df_gpa["Term"] >= "2017-fa" ]
df_gpa["Number"] = df_gpa["Number"].astype(str)
df_gpa["Course"] = df_gpa["Subject"] + " " + df_gpa["Number"]


def get_recent_average_gpa(course):
  df = df_gpa[ df_gpa["Course"] == course ].groupby("Course").agg("sum").reset_index()
  if len(df) == 0: return None

  df["Count GPA"] = df["A+"] + df["A"] + df["A-"] + df["B+"] + df["B"] + df["B-"] + df["C+"] + df["C"] + df["C-"] + df["D+"] + df["D"] + df["D-"] + df["W"]
  df["Sum GPA"] = (4 * (df["A+"] + df["A"])) + (3.67 * df["A-"]) + \
    (3.33 * df["B+"]) + (3 * df["B"]) + (2.67 * df["B-"]) + \
    (2.33 * df["C+"]) + (2 * df["C"]) + (1.67 * df["C-"]) + \
    (1.33 * df["D+"]) + (1 * df["D"]) + (0.67 * df["D-"])

  df["Average GPA"] = df["Sum GPA"] / df["Count GPA"]
  return df["Average GPA"].values[0]


def get_course_from_crn(crn):
    crn = int(crn)
    df_crnMatch = df_courseSchedule[ df_courseSchedule["CRN"] == crn ]
    if len(df_crnMatch) == 0: return None

    subject = df_crnMatch['Subject'].values[0]
    num = df_crnMatch['Number'].values[0]
    return subject + " " + str(num)


def format_reply_for_course(course):
  subject, number = course.split(" ")

  d = df_courseSchedule[ df_courseSchedule["Course"] == course ]
  if len(d) == 0: return None

  courseName = d["Name"].values[0]
  courseDescription = d["Description"].values[0]
  creditHours = d["Credit Hours"].values[0]
  courseScheduleURL = course_schedule_url_template.replace(":subject", subject).replace(":number", number)
  gpaVizURL = gpa_visualization_url_template.replace(":subject", subject).replace(":number", number)
  avgGPA = get_recent_average_gpa(course)
  if avgGPA == None:
    avgGPA = "*No recent GPA data available*"

  return f"[{course}]: {courseName} ({creditHours})\n" + \
    f"\n" + \
    f"^({courseDescription})\n" + \
    f"\n" + \
    f"- Offered in {courseScheduleTerm} -- (See: [Course Schedule]({courseScheduleURL}))\n" + \
    f"- Recent Average GPA: {avgGPA} -- (See: [GPA Visualization]({gpaVizURL}))"


def get_reply_from_submission(s, courses = []):
  courseInfos = []
  courses = []

  # Find all CRNs:
  re_crn = '\[(\d\d\d\d\d)\]'
  crnMatches = re.findall(re_crn, s)
  for crnMatch in crnMatches:
    crn = crnMatch
    course = get_course_from_crn(crn)
    if course != None and course not in courses:
      courseInfo = format_reply_for_course(course)
      if courseInfo != None:
        courseInfos.append(f"[{crn}] -> " + courseInfo)
        courses.append(course)

  # Find all courses:
  re_course = '\[(\w\w\w?\w?)\s?(\d\d\d)\]'
  courseMatches = re.findall(re_course, s)
  for courseMatch in courseMatches:
    subject = courseMatch[0]
    number = courseMatch[1]
    course = f"{subject} {number}"
    if course not in courses:
      courseInfo = format_reply_for_course(course)
      if courseInfo != None:
        courseInfos.append(courseInfo)

  # Join all the courseInfo strings together with an <hr> between them:
  return "\n\n---\n\n".join(courseInfos)