import csv
import pandas as pd
import numpy as np

def get_class(name, df):
    name_split = name.split()
    course = name_split[0]
    num = name_split[1]
    classes = df[(df["Subject"] == course) & (df["Number"] == int(num))]
    classes.groupby(['Subject', 'Number', 'Primary Instructor']).mean()
    classes = classes[['Primary Instructor', 'GPA']]
    return classes


def main():
    data = pd.read_csv ('/Users/rosenowak/Desktop/gpa-dataset.csv')
    df = pd.DataFrame(data, columns= ['Year','Term','YearTerm','Subject','Number','Course Title',
    'A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W','Primary Instructor', 'GPA'])
    print(get_class("CS 225", df))

main()
