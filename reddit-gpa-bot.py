import praw
import os
import time
import logging

from process_reddit_post import get_reply_from_submission


# Using .env file for instance-specific settings
from dotenv import load_dotenv
load_dotenv()

# Reddit Bot Init
bot = praw.Reddit(user_agent='UIUC GPA Bot v0.1',
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    username = os.getenv('REDDIT_USERNAME'),
    password= os.getenv('PASSWORD'))
subreddit = bot.subreddit(os.getenv('SUBREDDIT'))

comment_stream = subreddit.stream.comments(pause_after = -1)
submission_stream = subreddit.stream.submissions(pause_after = -1)

# Load cache of replied_to posts:
if not os.path.isfile("posts_replied_to.txt"):
  posts_replied_to = []
else:
  with open("posts_replied_to.txt", "r") as f:
    posts_replied_to = f.read()
    posts_replied_to = posts_replied_to.split("\n")
    posts_replied_to = list(filter(None, posts_replied_to))


# == Processing Logic ==
def processComment(commment):
  if comment.id in posts_replied_to:
    logging.debug(f"Skipping already replied to post {comment.id}")
    return

  if comment.author == "uiuc-bot":
    return

  logging.debug(f"Processing: {comment.id} by {comment.author}")

  # The content of the comment is the `body`  
  s = comment.body

  # Check if the bot should reply and log any replies:
  reply = get_reply_from_submission(s, comment.id)
  if reply:
    comment.reply(reply)
    logging.info(f"Replying to: {comment.id} by {comment.author}")
    posts_replied_to.append(comment.id)

def processSubmission(submission):
  if submission.id in posts_replied_to:
    logging.debug(f"Skipping already replied to post {comment.id}")
    return

  # Use both the title of the post and body:
  s = submission.title + " " + submission.selftext

  # Check if the bot should reply and log any replies:
  reply = get_reply_from_submission(s, submission.id)
  if reply:
    submission.reply(reply)
    logging.info(f"Replying to: {submission.title}")
    posts_replied_to.append(submission.id)  


# == "main" loop ==
while True:
  try:
    # Process any new comments:
    logging.debug(f"== Processing new comments ==")
    for comment in comment_stream:
      if comment is None:
        break
      processComment(comment)

    # Sleep a bit:
    time.sleep(5)

    # Process any new submissions (posts):
    logging.debug(f"== Processing new submissions ==")
    for submission in submission_stream:
      if submission is None:
        break
      processSubmission(submission)

    # Record any replies (for bot restart)
    with open("posts_replied_to.txt", "w") as f:
      for post_id in posts_replied_to:
        f.write(post_id + "\n")

    # Pause (30 seconds):
    logging.debug(f"Sleeping...")
    time.sleep(30)
  except Exception as e:
    logging.error(e, exc_info=True)
    time.sleep(60)
