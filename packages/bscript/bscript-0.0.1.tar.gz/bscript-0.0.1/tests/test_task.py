from bscript import task, Success, context

def test_basics():
    @task
    def toggle(on=1, off=0):
        yield off
        yield on
        # implicit return None / yield Success

    assert toggle() == 0
    assert toggle() == 1
    assert toggle() == Success
    assert toggle("on", "off") == "off"

def test_manual_reset():
    @task
    def counter():
        i = 0
        while True:
            yield i
            i += 1

    assert counter() == 0
    assert counter() == 1
    counter.reset()
    assert counter() == 0

def test_failure_reset():
    @task
    def blub():
        yield 0
        raise Exception
        yield 2

    assert blub() == 0
    try:
        blub()
        assert False
    except Exception:
        pass
    assert blub() == 0

def test_return_reset():
    @task
    def blub():
        yield 0
        return 1
        yield 2

    assert blub() == 0
    assert blub() == 1
    assert blub() == 0

def test_return_reset2():
    @task
    def blub():
        yield 0
        return
        yield 2

    assert blub() == 0
    assert blub() == None
    assert blub() == 0

def test_inactive_reset():
    @task(reset_after_inactivity=True) #type: ignore
    def counter():
        i = 0
        while True:
            yield i
            i += 1

    assert counter() == 0
    assert counter() == 1
    context().reset_inactive_states()
    assert counter() == 2
    context().reset_inactive_states()
    context().reset_inactive_states()
    assert counter() == 0

def test_inactive_reset_false():
    @task
    def counter():
        i = 0
        while True:
            yield i
            i += 1

    assert counter() == 0
    assert counter() == 1
    context().reset_inactive_states()
    context().reset_inactive_states()
    assert counter() == 2

def test_iter():
    @task
    def iter_test():
        yield 1
        yield 2
        yield 3

    assert list(iter_test) == [1, 2, 3]
