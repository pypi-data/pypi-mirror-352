import re

lines = open("outlaw.txt").read().split("\n")
lines = re.split(r'[\n.]',open("outlaw.txt").read())
spaces  = sorted([l.count(" ") for l in lines])
print(spaces)

shortened = [l for l in lines if l.count(" ") < 500]

splitted = []
for line in shortened:
    if line.

with open("outlaw_short.txt",'w',newline="\n") as f:
    f.write("\n".join(shortened))