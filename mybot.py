import praw
import pdb
import re
import os
import requests
import csv
import pandas as pd
import numpy as np

def get_class(name, df):
    name_split = name.split()
    course = name_split[0]
    num = name_split[1]
    classes = df[(df["Subject"] == course) & (df["Number"] == int(num))]
    classes = classes.groupby("Primary Instructor")['GPA'].mean()
    return classes

def from_crn(crn_num):
    data = pd.read_csv ('/Users/rosenowak/Desktop/2019-fa.csv')
    df = pd.DataFrame(data)
    crn = '47100'
    crn = int(crn)
    temp = df[(df["CRN"] == crn)]
    subject = temp['Subject'].values[0]
    num = temp['Number'].values[0]
    return subject + " " + str(num)

def main():
    print("here")
    data = pd.read_csv ('/Users/rosenowak/Desktop/gpa-dataset.csv')
    df = pd.DataFrame(data)
    df = df[ df["YearTerm"] >= '2017-fa' ]

    # URL = "https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey=4bd28adf5fa21a0f3bd9b153eda5"
    # partners = ""
    # PARAMS = {'partners':partners}
    # r = requests.get(url = URL, params = PARAMS)
    # data = r.json()
    # people = data['partners']


    bot = praw.Reddit(user_agent='classes v0.1',
                  client_id='XoDRN8nBSmglSg',
                  client_secret='RBW92Bu-hmwaMnXIs74VLB2n-V4',
                  username='classbotuiuc',
                  password='lovecs225')

    print("here1")

    subreddit = bot.subreddit('testingground4bots')
    comments = subreddit.stream.comments()

    # Have we run this code before? If not, create an empty list
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []

    # If we have run the code before, load the list of posts we have replied to
    else:
        # Read the file into a list and remove any empty values
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    # Get the top 5 values from our subreddit
    for submission in subreddit.new(limit=50):
        print("here2")

        if submission.id not in posts_replied_to:
            #r"\[((/w+)()?(/d+))\]"
            if re.search("How is it?", submission.title, re.IGNORECASE):
                print("here5")
                result = re.search('/[(/w+)()?(/d+/)]', submission.title)
                #lookup = result.group(0) + result.group(1) + result.group(2)
                answer = get_class("CS 225", df)
                new_answer = answer.to_string()

                submission.reply(new_answer)
                print("Bot replying to : ", submission.title)
                posts_replied_to.append(submission.id)
            elif re.search('/[/d/d/d/d/d]', submission.title, re.IGNORECASE):
                print("here6")
                result = re.search('/[/d/d/d/d/d]', submission.title)
                lookup = from_crn(result.group(0))
                submission.reply(get_class(lookup))
                print("Bot replying to : ", submission.title)
                posts_replied_to.append(submission.id)


    # Write our updated list back to the file
    with open("posts_replied_to.txt", "w") as f:
        print("here3")

        for post_id in posts_replied_to:
            f.write(post_id + "\n")



main()
