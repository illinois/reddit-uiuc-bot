import praw

bot = praw.Reddit(user_agent='classes v0.1',
                  client_id='XoDRN8nBSmglSg',
                  client_secret='RBW92Bu-hmwaMnXIs74VLB2n-V4',
                  username='classbotuiuc',
                  password='lovecs225')


subreddit = bot.subreddit('uiuc')
comments = subreddit.stream.comments()

for comment in comments:
    text = comment.body # Fetch body
    author = comment.author # Fetch author
    if 'fialed' in text.lower():
        # Generate a message
        #message = "Why no love for Titan, u/{0} ?".format(author)
        message = "Oof"
        comment.reply(message) # Send message
