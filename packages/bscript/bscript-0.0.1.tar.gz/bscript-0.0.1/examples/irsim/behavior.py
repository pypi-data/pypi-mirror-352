from bscript import Running, input, task
from behavior_utils import drive_to

@task
def follow_path():
    idx = 0
    while True:
        while drive_to(input().path[idx]): yield Running
        idx = (idx + 1) % len(input().path)

@task
def charging():
    if input().battery < 25:
        while drive_to(input().socket): yield Running
        while input().battery < 100: yield Running

def root_behavior():
    if not charging(): follow_path()
