import pandas as pd
import re
import logging
logging.basicConfig(level=logging.DEBUG)

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

df_gened = pd.read_csv('gen-ed.csv')

df_fa19 = pd.read_csv('uiuc-course-catalog-fa19.csv')
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
  df = df_gened[ df_gened["Course"] == course ]
  if len(df) == 0: return None

  gen_eds_offered = []
  if not df["ACP"].empty:
      gen_eds_offered.append("Advance Composition")
  if not df["CS"].empty:
      gen_eds_offered.append("Cultural Studies")
  if not df["HUM"].empty:
      gen_eds_offered.append("Humanities")
  if not df["NAT"].empty:
      gen_eds_offered.append("Natural Sciences")
  if not df["QR"].empty:
      gen_eds_offered.append("Quantitative Reasoning")
  if not df["SBS"].empty:
      gen_eds_offered.append("Social & Behavior")

  if gen_eds_offered == None:
      return None

  gen_ed_formatted = ""
  if len(gen_eds_offered) > 1:
      for i in range(len(gen_eds_offered) - 1):
          gen_ed_formatted += gen_eds_offered[i]
          gen_ed_formatted += ", "
  gen_ed_formatted += gen_eds_offered[len(gen_eds_offered)-1]

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
  else:
      courseName = d["Name"].values[0]
      creditHours = d["Credit Hours"].values[0]
      courseScheduleURL = course_schedule_url_template.replace(":subject", subject).replace(":number", number)

  gen_eds = get_all_geneds(course)
  if gen_eds == None:
      gen_eds = "*No gen eds are fullfilled*"
  gpaVizURL = gpa_visualization_url_template.replace(":subject", subject).replace(":number", number)
  avgGPA = get_recent_average_gpa(course)
  if avgGPA == None:
    avgGPA = "*No recent GPA data available*"
  else:
    avgGPA = round(avgGPA, 2)

  logging.debug(f"Course Found: {course}")
  if len(d) > 0:
      return f"**\[{course}\]**: **{courseName}** -- {creditHours}\n" + \
        f"- ✅ Offered in {courseScheduleTerm} -- [Course Schedule for {course}]({courseScheduleURL})\n" + \
        f"- Recent Average GPA: **{avgGPA}** -- [GPA Visualization for {course}]({gpaVizURL})\n"+ \
        f"- Gen Eds Fullfilled: {gen_eds}\n"
  else:
      return f"**\[{course}\]**: **{courseName}** -- {creditHours}\n" + \
        f"- ❌ Not offered in {courseScheduleTerm}\n" + \
        f"- Recent Average GPA: **{avgGPA}** -- [GPA Visualization for {course}]({gpaVizURL})\n"+ \
        f"- Gen Eds Fullfilled: {gen_eds}\n"




def get_reply_from_submission(s, id=-1):
  courseInfos = []
  courses = []

  # Find all CRNs:
  re_crn = '\[(\d{5})\]'
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
  re_course = '\[([A-Za-z]{2,4})\s?(\d{3})\]'
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
