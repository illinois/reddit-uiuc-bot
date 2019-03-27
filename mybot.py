import praw
import pdb
import re
import os

bot = praw.Reddit(user_agent='classes v0.1',
                  client_id='XoDRN8nBSmglSg',
                  client_secret='RBW92Bu-hmwaMnXIs74VLB2n-V4',
                  username='classbotuiuc',
                  password='lovecs225')


subreddit = bot.subreddit('fourpanelcringe')
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
for submission in subreddit.new(limit=5):
    if submission.id not in posts_replied_to:
        if re.search("Sublease", submission.title, re.IGNORECASE):
            submission.reply("No")
            print("Bot replying to : ", submission.title)
            posts_replied_to.append(submission.id)

# Write our updated list back to the file
with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")

#for comment in comments:
#    text = comment.body # Fetch body
#    author = comment.author # Fetch author
#    if 'fialed' in text.lower():
#        # Generate a message
#        #message = "Why no love for Titan, u/{0} ?".format(author)
#        message = "Oof"
#        comment.reply(message) # Send message
