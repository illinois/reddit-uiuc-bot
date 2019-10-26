import praw
import pdb
import re
import os
import requests
import csv
import pandas as pd
import numpy as np
from process_reddit_post import get_reply_from_submission

df = pd.read_csv('gpa-dataset.csv')
df = df[ df["YearTerm"] >= '2017-fa' ]


# Reddit Bot Init
bot = praw.Reddit(user_agent='classes v0.1',
    client_id='XoDRN8nBSmglSg',
    client_secret='RBW92Bu-hmwaMnXIs74VLB2n-V4',
    username='classbotuiuc',
    password='lovecs225')
subreddit = bot.subreddit('testingground4bots')
comments = subreddit.stream.comments()

# Load cache of replied_to posts:
if not os.path.isfile("posts_replied_to.txt"):
  posts_replied_to = []
else:
  with open("posts_replied_to.txt", "r") as f:
    posts_replied_to = f.read()
    posts_replied_to = posts_replied_to.split("\n")
    posts_replied_to = list(filter(None, posts_replied_to))

# Bot Logic/Processing
for submission in subreddit.new(limit=20):
  if submission.id not in posts_replied_to:
    # Use both the title of the post and body:
    s = submission.title + " " + submission.selftext
    reply = get_reply_from_submission(s, submission.id)

    # Reply and record reply:
    if reply:
      submission.reply(reply)
      print(f"Bot replying to: {submission.title}")
    
    posts_replied_to.append(submission.id)

with open("posts_replied_to.txt", "w") as f:
  for post_id in posts_replied_to:
    f.write(post_id + "\n")
