from bscript import input, task
from bscript.btree import forever, sequence, decorate
from behavior_utils import drive_to

@task
def follow_path():
    idx = 0

    def drive_to_next_point():
        return drive_to(input().path[idx])

    def select_next_point():
        nonlocal idx
        idx = (idx + 1) % len(input().path)

    def follow_section():
        yield from sequence(drive_to_next_point, select_next_point)

    yield from forever(follow_section)

def drive_to_socket(): return drive_to(input().socket)
def recharge(): return input().battery < 100

@task
def ensure_charged():
    if input().battery < 25:
        yield from sequence(drive_to_socket, recharge)

@task
def root_behavior():
    yield from decorate(ensure_charged, follow_path)
