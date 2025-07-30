from dataclasses import dataclass
from typing import Any
from bscript import fsm, initial, Transition

def test_toggle():
    @fsm
    @dataclass
    class toggle_fsm:
        # parameter with type annotations!
        on: Any = 1
        off: Any = 0

        # internal state(s) without type annotations
        last_state = None

        @initial
        def off_state(self):
            # decision
            if self.last_state == self.off_state:
                return Transition(self.on_state)

            # action
            self.last_state = self.off_state
            return self.off

        def on_state(self):
            # decision
            if self.last_state == self.on_state:
                return Transition(self.off_state)

            # action
            self.last_state = self.on_state
            return self.on

    assert toggle_fsm() == 0
    assert toggle_fsm() == 1
    assert toggle_fsm() == 0
    assert toggle_fsm("on", "off") == "on"


def test_stop_iteration():
    @fsm
    class done_fsm:
        c = 0

        @initial
        def _(self):
            if self.c >= 2: raise StopIteration()
            self.c += 1
            return self.c

    assert done_fsm() == 1
    assert done_fsm() == 2
    assert done_fsm() == None
    assert done_fsm() == 1


def test_iter():
    @fsm
    class iter_fsm:
        c = 0

        @initial
        def _(self):
            if self.c >= 3: raise StopIteration()
            self.c += 1
            return self.c

    assert list(iter_fsm) == [1, 2, 3]

#todo test generator
