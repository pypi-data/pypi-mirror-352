## Details


### state machines

a finite state machine implementing a simple hysteresis

```python
@bscript.fsm
class Hysteresis:
    #parameters must have type annotations
    val: float = 0

    @bscript.initial
    def initial(self):
        return bscript.Transition(self.minus if self.val < 0 else self.plus)

    def plus(self):
        if self.val < -0.5:
            return bscript.Transition(self.minus)
        return 1

    def minus(self):
        if self.val > 0.5:
            return bscript.Transition(self.plus)
        return -1

assert Hysteresis(  0) ==  1
assert Hysteresis(-.4) ==  1
assert Hysteresis(-.6) == -1
assert Hysteresis( .4) == -1
assert Hysteresis( .6) ==  1
```


### context handling

```python
ctx1 = bscript.bScriptContext()

@bscript.task
def toggle():
    yield 0
    yield 1

assert ctx1.execute(toggle) == 0
assert toggle() == 0 # default context
assert ctx1.execute(toggle) == 1
assert toggle() == 1 # default context
```


### input & output

global `input` (world model) and `output` (action selection) are available through the `context`:

```python
ctx = bscript.context()
ctx.input = 5 # -> world model
ctx.output = {} # -> action selection

# run behaviors, call bscript.input() / bscript.output() from anywhere
def foo():
    bscript.output()["double"] = bscript.input() * 2

foo()
assert ctx.output == {'double': 10}
```


### manual resetting states

```python
@bscript.task
def counter():
    for i in range(99):
        yield i

ctx = bscript.context()

assert counter() == 0
assert counter() == 1

ctx.reset_state(counter)

assert counter() == 0
```


### resetting inactivity states

as other behavior speicification languages bscript can reset
"inactive" _tasks_ (and state machines) with
`context.reset_inactive_states()`. A _task_ (or state machine) is
considered inactive if it was not called since the last call to
`reset_inactive_states` (or since the start of the program).

This only applies to _tasks_ and state machines with `reset_after_inactivity=True` (default is `False`).

```python
@bscript.task(reset_after_inactivity=True)
def counter1():
    for i in range(99): yield i

assert counter1() == 0

bscript.context().reset_inactive_states() # frame

assert counter1() == 1 # was active in last frame

bscript.context().reset_inactive_states() # frame
bscript.context().reset_inactive_states() # frame

counter1() == 0 # was inactive in last frame
```


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


