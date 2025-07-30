

@task
def next_point():
    idx = 0
    point = lambda: input().path[idx].state

    while True:
        if target_reached(point()):
            idx = (idx + 1) % len(input().path)
        yield point()

def follow_path():
    drive_to(next_point())

