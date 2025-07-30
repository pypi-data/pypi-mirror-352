from bscript import Failure, task, Running, sequence, fallback

@task
def foo():
    for _ in range(2):
        print("foo"); yield Running

@task
def bar():
    for _ in range(2):
        print("bar"); yield Running

@task
def fail():
    raise Failure
    yield 1

@task
def yf_test():
    yield from foo
    yield from bar

@task
def seq_test():
    yield from sequence(foo, bar)

@task
def fallback_test():
    yield from fallback(foo, fail)
    yield from fallback(fail, bar)


while yf_test(): pass
while seq_test(): pass
while fallback_test(): pass
