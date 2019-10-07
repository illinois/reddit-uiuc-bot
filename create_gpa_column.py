import csv
import pandas as pd
import numpy as np

def main():
    data = pd.read_csv ('/Users/rosenowak/Desktop/uiuc-gpa-dataset.csv')
    df = pd.DataFrame(data, columns= ['Year','Term','YearTerm','Subject','Number','Course Title',
    'A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W','Primary Instructor'])
    df['GPA'] = (((df['A+']*4) + (df['A']*4) + (df['A-']*3.67) + (df['B+']*3.33) + (df['B']*3) +
    (df['B-']*2.67) + (df['C+']*2.33) + (df['C']*2) + (df['C-']*1.67) + (df['D+']*1.33) + (df['D']) + (df['D-']*0.67))
    /((df['A+']) + (df['A']) + (df['A-']) + (df['B+']) + (df['B']) +
    (df['B-']) + (df['C+']) + (df['C']) + (df['C-']) + (df['D+']) + (df['D']) + (df['D-']) + (df['F'])))
    df.to_csv('/Users/rosenowak/Desktop/gpa-dataset.csv')

main()
