from inspect import isfunction, isgenerator, isgeneratorfunction
from bscript import Failure

def _exec_task(t):
    if isgeneratorfunction(t):
        t_inst = t()
        yield from t_inst
    elif not isfunction(t):
        yield from t
    else:
        while (r := t()): yield r

def sequence(*tasks):
    for t in tasks:
        yield from _exec_task(t)

def fallback(*tasks):
    for t in tasks:
        try:
            yield from _exec_task(t)
            return
        except Failure:
            pass

    raise Failure()

def forever(task):
    assert not isgenerator(task)
    while True:
        yield from _exec_task(task)

def decorate(task, *others):
    assert not isgeneratorfunction(task)
    assert not isgenerator(task)
    while True:
        if not (r := task()):
            for o in others:
                o()
        yield r
