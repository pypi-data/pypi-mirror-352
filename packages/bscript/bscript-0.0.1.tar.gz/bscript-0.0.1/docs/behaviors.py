### bscript

from bscript import task, Running, Success, Failure

### python functions
#
# basic (and in this context important) properties of python functions

def foo():
    pass

def bar():
    return

def blub():
    return 1

assert foo() == None
assert bar() == None
assert blub() == 1

### tasks
#
# _tasks_ are generators but they can be called "like functions". They have a
# global state and their parameters get updated at each call. You can think of
# them as somekind of _singleton_ or a _skill_. A "function with an internal
# state" or a "function" with `yield` statements.
#
# basic properties similar to functions:

@task
def bla():
    yield 1

assert bla() == 1
assert bla() == None

@task
def foobar():
    yield 1
    yield 2
    return
    yield 3

assert foobar() == 1
assert foobar() == 2
assert foobar() == None
assert foobar() == 1

@task
def foox(x):
    yield x
    yield x

assert foox(4) == 4
assert foox(9) == 9
assert foox(1) == None


# In python generators (and therefor in _tasks_) `yield` and `return`
# statements can be mixed, they behave as expected. `yield` returns a value and
# resumes the execution. `return` returns a value and restarts the execution.
#
# _task_ add these properties ontop of python generators:
#     - implicit context management for the generator states
#     - automatic handling of `StopIteration` as a function like `return` statement
#     - update parameters on each call

### finite state machin-ish nodes
#
# are available

### `Running`, `Success`, `Failure`

# inspired by behavior trees, `bscript` defines the states `Running`, `Success`
# and `Failure`. They are defined like this:

assert Running is True
assert Success is None
assert Failure is Exception

Since each python function (or _tasks_) always returns something -- explicitly or
implicitly -- this has pretty interesting effects:

    - if a function or _task_ returns anything other than `None` (`== Success == not Running`)
        -it's state is `Running == not Success(ful yet)` (or _active_)

    - a functions (or _task_) that does not return anything (explicitly) returns `None`
        - `None == Success == not Running` (or _not active_)

    - `while do_something()` is equivalent to
        - `while do_something() is Running`
        - `while do_something() is not Success(ful)`

    - `if something()` is equivalent to:
        - `if something() is Running`
        - `if something() is not Success(ful)`

    - `do_something() and do_something_else()` is equivalent to
        - if do_something() is Running: do_something_else()
        - `if do_something() is not Success(ful): do_something_else()`

    - `do_something() or do_something_else()` is equivalent to
        - `if do_something is not Running: do_something_else()`
        - `if do_something() is Success(ful): do_something_else()`

all those "sentences" are valid python code and actually work when all nodes only use
`Running` and `Success` as return values

These are the basic building blocks for behaviors with functions and _tasks_.

### actions

low level nodes that execute actions can often be written as regular functions:

    def drive_to(target):
        output().target = target
        return Success if target_reached(target) else Running

or as a _task_:

    @task
    def drive_to(target):
        while not target_reached(target):
            output().target = target
            yield Running

        # Success (implicit return None)


### high level behaviors

#### sequence of sub behaviors

    @task
    def consume_banana():
        while peal_banana(): yield Running
        while eat_banana(): yield Running

#### failures and fallbacks

If a (sub) behavior raises a `Failure` (`Exception`) it traverse upwards the call tree until it gets caught and handles -- as exceptions naturally do, which complies with behavior trees and makes a lot of sense in behaviors

    @task
    def eat():
        try:
            while consume_banana(): yield Running
        except Failure:
            while eat_apple(): yield Running

#### parallel execution of behaviors

the body of the while loop....

    @task
    def goto_work():

        while walk_to(bus_stop): listen_to_music() and eat_apple()
            yield Running

        while sit_in_bus(): listen_to_music() and (check_mails() or idle())
            yield Running


### conditions

    @task
    def emergency():
        if random() > 0.9:
            yield "ALARM"
            yield "ALARM"

        # implicit return None == not Running

    def some_behavior():
        if emergency():
            run_away()
            return Running
        else:
            return do_something()

this is similar to behavior tree decorators


### while & yield

I guess it's best practice to use simple straight forward `while` / `yield` combinations. I would suggest to try to stick as close as possible to a simple while loop with an uncoditional `yield`:

    while something:
        ...
        yield Running


