## bscript

Only works with `python>=3.13`.

`bscript` is a behavior specification library for agents respectively robots.
It is similar to hierarchical finite state machine approaches, but primarily
uses decorated python generators -- called _tasks_ -- instead of finite state
machines. Withit `bscript` enables an imperative scripting like approach to
behavior engineering.

_tasks_ are callable _singletons_ which wrap a global generator state for each
underlying generator. These "_state based functions_" can be used to describe
complex and deliberate hierarchical behaviors.

```python
from bscript import task, Running

@task
def travel():
    while walk_to(next_bus_stop()): listen_to_music() and eat_an_apple()
        yield Running

    while not destination_reached(): sit_in_bus() and (read_a_book() or idle())
        yield Running

    while enjoy(): stay()
        yield Running
    ...
```

this should pretty much do what you literally read....


### python functions

(in this context particular important) properties of regular python functions
(and _tasks_ aswell)

```python
def foo():
    pass

assert foo() == None

def bar():
    return

assert bar() == None
```


### tasks

_tasks_ are generators that can be called "like functions". They have a
global state each and their parameter get updated at each call. _tasks_ are
implemented as callable _singeltons_. Furthermore they update their parameters
(local variables inside the generator namespace) at each call and a
`StopIteration` is transformed into a `return` statement like behavior.

A _task_ is pretty much a "function with an internal state" or a "function"
with `yield` statements".

`yield` and `return` statements can be mixed inside python generators -- and
therefor inside _tasks_ aswell. They behave as expected:
    - `yield` returns a value and resumes the execution
    - `return` returns a value and restarts the execution

the result is somehow similar to functions:

```python
@task
def bla():
    yield 1

assert bla() == 1
assert bla() == None

@task
def foobar():
    yield 1
    yield 2
    return 99
    yield 4

assert foobar() == 1
assert foobar() == 2
assert foobar() == 99
assert foobar() == 1

@task
def foox(x):
    yield x
    yield x

assert foox(4) == 4
assert foox(9) == 9
assert foox(1) == None
```

### `Running`, `Success`, `Failure`

inspired by behavior trees, `bscript` defines the states `Running`, `Success`
and `Failure`. It turned out to be really convenient to define them like this:

```python
Running = True
Success = None
class Failure(Exception): ...
```

These definitions have pretty interesting properties, especially since each
python function (and _task_) always returns something -- explicitly or
implicitly `None`.

#### Properties:

```python
assert not Running is Success
assert not Success is Running

def always_successful():
    pass
    # implicit return None

def always_running():
    return not None

assert always_successful() is Success
assert always_successful() is not Running

assert always_running() is Running
assert always_running() is not Success
```

- `while do_something()` is equivalent to
    - `while do_something() is Running`
    - `while do_something() is not Success`

- `if something()` is equivalent to:
    - `if something() is Running`
    - `if something() is not Success`

- `do_something() and do_something_else()` is equivalent to
    - `if do_something() is Running: do_something_else()`
    - `if do_something() is not Success: do_something_else()`

- `do_something() or do_something_else()` is equivalent to
    - `if do_something() is not Running: do_something_else()`
    - `if do_something() is Success: do_something_else()`

- a `Failure` is _raised_ and traverses up the behavior tree until it gets caught

All those _sentences_ are valid python code and actually work when all nodes
use `Running` and `Success` as return values.

These are the basic building blocks for behaviors with `bscript`.

### actions

low level nodes that execute actions can often be written as regular functions:

```python
def drive_to(target):
    output().target = target
    return Success if target_reached(target) else Running
```

or as a _task_:

```python
@task
def drive_to(target):
    while not target_reached(target): output().target = target
        yield Running

    # Success (implicit return None / Success)
```


### high level behaviors

#### sequence of sub behaviors

```python
@task
def eat():
    while peal_banana(): yield Running
    while eat_banana(): yield Running

    # Success (implicit return None / Success)
```

#### failures and fallbacks

If a (sub) behavior raises a `Failure` (`Exception`) it traverse upwards the
call tree until it gets caught and handled -- as exceptions naturally do, which
complies with behavior tree failures and makes a lot of sense in behaviors:

```python
@task
def eat():
    try:
        while eat_banana(): yield Running
    except Failure:
        while eat_apple(): yield Running
```

#### parallel execution of behaviors

the body of the while loop....

```python
@task
def travel():
    while walk_to(next_bus_stop()): listen_to_music() and eat_an_apple()
        yield Running

    while not destination_reached(): sit_in_bus() and (read_a_book() or idle())
        yield Running

    ...
```

### conditions

```python
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
```

this is similar to behavior tree decorators


### while & yield

I guess it's best practice to use simple straight forward `while` / `yield`
combinations. I would suggest to try to stick as close as possible to a simple
while loop with an uncoditional `yield`:

```python
while something:
    ...
    yield Running
```


### raw python generators

until you really not what you're doing avoid using regular python generators in
these behaviors. This includes `for x in ...` loops which create generators /
iterators which can have strange side effects with changing parameters of
_task_. Avoid them if possible....


### finite state machin-ish nodes

are available

```python
from bscript.extensions.state_machines import fsm, initial, Transition
```
