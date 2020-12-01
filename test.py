
from process_reddit_post import get_reply_from_submission

def test(s):
  print(f"=== Input: {s} ===")
  r = get_reply_from_submission(s)
  #print(r)

test("[CS 225] is a course!")
test("[CS 225] [CS 233] makes it two courses.")
test("[CS 107] is another course.")
test("[STAT 107] is another course.")
test("[ECE 107] is another course.")
test("[70340] is the CRN.")



test("[00000] is the CRN.")
test("[CS225] [CS225]")
test("[CS225] [CS225] [CS 225]")
test("[CS  225]")
test("CS 225")

test("[cs225]")

test("[CS 499] [43753] [66333] [CS 374]")


test("The quick brown fox jumped over the lazy red dog.")

# Should not have a GPA:
test("[ABE 457]")
