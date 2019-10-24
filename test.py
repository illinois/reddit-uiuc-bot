
from process_reddit_post import get_reply_from_submission

def test(s):
  print(f"=== Input: {s} ===")
  print(get_reply_from_submission(s))

test("[CS 225] is a course!")
test("[CS 225] [CS 233] makes it two courses.")
test("[CS 107] is another course.")
test("[70340] is the CRN.")

