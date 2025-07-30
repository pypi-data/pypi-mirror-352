# bscript

[![PyPI - Version](https://img.shields.io/pypi/v/bscript.svg)](https://pypi.org/project/bscript)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bscript.svg)](https://pypi.org/project/bscript)

-----

## Table of Contents

- [bscript](#bscript)
- [Installation](#installation)
- [Basics](#Basics)
- [Examples](#Examples)
- [License](#license)

## bscript

Only works with `python>=3.13`.

`bscript` is a behavior specification library for agents respectively robots.
It is similar to hierarchical finite state machine approaches, but primarily
uses decorated python generators -- called _tasks_ -- instead of finite state
machines.
`bscript` enables an imperative scripting like approach to behavior
engineering.

_tasks_ are callable _singletons_ which wrap a "global" generator state for each
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
    ...
```

this should pretty much do what you literally read....


## Installation

```console
pip install bscript
```

## Basics


### python functions

in this context particular important properties of regular python functions
(and _tasks_ aswell)

```python
def foo():
    pass
    # implicit return None

assert foo() == None

def bar():
    return # implicit None

assert bar() == None
```


### tasks

_tasks_ are generators -- a super set of functions -- that can be called "like
functions". They have a global state each and their parameter get updated at
each call. _tasks_ are implemented as callable _singeltons_. Furthermore they
update their parameters (local variables inside the generator namespace) at
each call and a `StopIteration` is transformed into a `return` statement like
behavior.

A _task_ is pretty much a "function with an internal state" or a "function
with `yield` statements".

`yield` and `return` statements can be mixed inside python generators -- and
therefor inside _tasks_ aswell. They behave as expected:

- `yield` returns a value and resumes the execution
- `return` returns a value and restarts the execution

the result is pretty similar to functions:

```python
from bscript import task

@task
def foo_pass():
    pass

assert foo_pass() == None

@task
def foo_return():
    return 1

assert foo_return() == 1

@task
def foo_yield():
    yield 1

assert foo_yield() == 1
assert foo_yield() == None

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
and `Failure`. It turns out defining them like this...

```python
Running = True
Success = None
class Failure(Exception): ...
```

...has pretty interesting properties, especially since each
function or _task_ always returns something -- explicitly or implicitly
`None` (which is equivalent to `Success`):

```python
from bscript import Running, Success

assert Running is not Success
assert Success is not Running

def always_successful():
    pass
    # implicit return None / Success

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

These are the basic building blocks for `bscript` behaviors.

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
    while not target_reached(target):
        output().target = target
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

```python
@task
def travel():
    while walk_to(next_bus_stop()): listen_to_music() and eat_an_apple()
        yield Running

    while not destination_reached(): sit_in_bus() and (read_a_book() or idle())
        yield Running

    ...
```

#### conditions

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


### finite state machin-ish nodes, context handling, input & output and more

-> `docs/details.md`


## Examples

The [lunch
behavior](https://github.com/jeff-dh/bscript/blob/main/examples/have_lunch.py)
and the [irsim
behavior](https://github.com/jeff-dh/bscript/blob/main/examples/irsim/behavior.py)
show basic example applications.


## License

`bscript` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
