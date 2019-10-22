import pandas as pd
import re

def get_class(name, df):
    name_split = name.split()
    course = name_split[0]
    num = name_split[1]
    classes = df[(df["Subject"] == course) & (df["Number"] == int(num))]
    classes = classes.groupby("Primary Instructor")['GPA'].mean().reset_index()
    return classes

#data = pd.read_csv ('gpa-dataset.csv')
#df = pd.DataFrame(data)
#df = df[ df["YearTerm"] >= '2017-fa' ]

#d = get_class("CS 225", df)

#print(s)


s = "this is a title [CS 415] [MATH 225] yah yah"

# Regex for Course String:
re_course = '\[(\w\w\w?\w?)\s?(\d\d\d)\]'

all_matches = re.findall(re_course, s)
for match in all_matches:
  subject = match[0]
  number = match[1]
  course = f"{subject} {number}"
  print(course)

# r = re.search(re_course, s, re.IGNORECASE)
# print(r)
# if r:
#   subject = r.group(1)
#   number = r.group(2)
#   course = f"{subject} {number}"
#   print(course)
# else:
#   print(":(")

# Regex for CRN:
s = "[23456]"

r = re.search('\[(\d\d\d\d\d)\]', s, re.IGNORECASE)
if r:
  crn = r.group(1)
  print(crn)
else:
  print(":(")