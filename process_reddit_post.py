import pandas as pd
import re
import math

import logging
logging.basicConfig(level=logging.DEBUG)

course_schedule_url_template = "https://courses.illinois.edu/schedule/2020/fall/:subject/:number"
gpa_visualization_url_template = "https://waf.cs.illinois.edu/discovery/grade_disparity_between_sections_at_uiuc/?subj=:subject&course=:number"

courseScheduleTerm = "Fall 2020"

df_courseSchedule = pd.read_csv('data/2020-fa.csv')
df_courseSchedule["Number"] = df_courseSchedule["Number"].astype(str)
df_courseSchedule["Course"] = df_courseSchedule["Subject"] + " " + df_courseSchedule["Number"]

df_gpa = pd.read_csv('data/uiuc-gpa-dataset.csv')
df_gpa = df_gpa[ df_gpa["Term"] >= "2017-fa" ]
df_gpa["Number"] = df_gpa["Number"].astype(str)
df_gpa["Course"] = df_gpa["Subject"] + " " + df_gpa["Number"]

df_gened = pd.read_csv('data/gen-ed.csv')

df_fa19 = pd.read_csv('data/uiuc-course-catalog-fa19.csv')
df_fa19["Number"] = df_fa19["Number"].astype(str)
df_fa19["Course"] = df_fa19["Subject"] + " " + df_fa19["Number"]

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


def get_all_geneds(course):
  df = df_courseSchedule[ df_courseSchedule["Course"] == course ]
  if len(df) == 0: return None

  gened = df["Degree Attributes"]
  if len(gened) == 0:
      return None

  gened = gened.values[0]
  gen_eds_offered = []
  logging.debug(f"GenEds String: {gened}")

  if str(gened) != "nan":
    if "Advanced Composition" in gened:
        gen_eds_offered.append("Advance Composition")
    if "Cultural Studies" in gened:
        gen_eds_offered.append("Cultural Studies")
    if "Humanities" in gened:
        gen_eds_offered.append("Humanities")
    if "Natural Sciences" in gened:
        gen_eds_offered.append("Natural Sciences")
    if "Quantitative Reasoning" in gened:
        gen_eds_offered.append("Quantitative Reasoning")
    if "Social & Behavior" in gened:
        gen_eds_offered.append("Social & Behavior")

  if len(gen_eds_offered) == 0:
    return None

  gen_ed_formatted = ",".join(gen_eds_offered)
  logging.debug(f"GenEds Found: {gen_ed_formatted}")
  return gen_ed_formatted


def get_course_from_crn(crn):
    crn = int(crn)
    df_crnMatch = df_courseSchedule[ df_courseSchedule["CRN"] == crn ]
    if len(df_crnMatch) == 0:
      logging.debug(f"No CRN Found: {crn}")
      return None

    subject = df_crnMatch['Subject'].values[0]
    number = df_crnMatch['Number'].values[0]
    course = f"{subject} {number}"

    logging.debug(f"CRN Found: {crn} -> {course}")
    return course


def format_reply_for_course(course):
  subject, number = course.split(" ")

  d = df_courseSchedule[ df_courseSchedule["Course"] == course ]
  actual_class = df_fa19[ df_fa19["Course"] == course ]
  if len(d) == 0 and len(actual_class) == 0:
    logging.debug(f"No Course Found: {course}")
    return None

  if len(d) == 0:
      courseName = actual_class["Name"].values[0]
      creditHours = actual_class["Credit Hours"].values[0]
      gen_eds = get_all_geneds(actual_class)
  else:
      courseName = d["Name"].values[0]
      creditHours = d["Credit Hours"].values[0]
      courseScheduleURL = course_schedule_url_template.replace(":subject", subject).replace(":number", number)
      gen_eds = get_all_geneds(course)

  gpaVizURL = gpa_visualization_url_template.replace(":subject", subject).replace(":number", number)
  avgGPA = get_recent_average_gpa(course)


  logging.debug(f"Course Found: {course}")

  # Course Info:
  response = f"**\[{course}\]**: **{courseName}** -- {creditHours}"

  # Course Offering Term:
  if len(d) > 0:
    response += f" -- ✅ [Offered in {courseScheduleTerm}]({courseScheduleURL})"
  else:
    response += f" -- ❌ Not offered in {courseScheduleTerm}"

  # Course GPA:
  if avgGPA == None:
    response += f" -- No recent GPA data"
  else:
    avgGPA = round(avgGPA, 2)
    response += f" -- [Recent Average GPA]({gpaVizURL}): **{avgGPA}**"

  # GenEd Info:
  if gen_eds != None:
    response += f" -- GenEds: {gen_eds}"

  return response


def get_reply_from_submission(s, id=-1):
  logging.debug(f"Message: {s}")
  courseInfos = []
  courses = []

  # Find all CRNs:
  re_crn = '\\\\?\[(\d{5})\\\\?\]'
  crnMatches = re.findall(re_crn, s)
  for crnMatch in crnMatches:
    crn = crnMatch
    logging.info(f"[{id}] CRN Match: {crn}")

    course = get_course_from_crn(crn)
    if course != None and course not in courses:
      courseInfo = format_reply_for_course(course)
      if courseInfo != None:
        courseInfos.append(f"**\[{crn}\]** -> " + courseInfo)
        courses.append(course)
        logging.info(f"[{id}] Output: {course}")


  # Find all courses:
  re_course = '\\\\?\[([A-Za-z]{2,4})\s?(\d{3})\\\\?\]'
  courseMatches = re.findall(re_course, s)
  for courseMatch in courseMatches:
    subject = courseMatch[0].upper()
    number = courseMatch[1]
    course = f"{subject} {number}"
    logging.info(f"[{id}] Course Match: {course}")

    if course not in courses:
      courseInfo = format_reply_for_course(course)
      if courseInfo != None:
        courseInfos.append(courseInfo)
        courses.append(course)
        logging.info(f"[{id}] Output: {course}")

  # Prevent the output from being HUGE
  if len(courseInfos) > 10:
    courseInfos = courseInfos[0:9]

  # Join all the courseInfo strings together with an <hr> between them:
  if len(courseInfos) == 0:
    return None
  else:
    return "\n\n---\n\n".join(courseInfos)
