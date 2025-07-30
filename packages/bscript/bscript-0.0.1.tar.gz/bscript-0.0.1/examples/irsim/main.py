import dataclasses
from irsim.util.util import relative_position
import numpy as np
import irsim
import irsim.lib
import bscript

# from behavior import root_behavior
from bt_behavior import root_behavior
# from fsm_behavior import root_behavior

battery = 100
socket = np.array([[5],[5],[0]])

@dataclasses.dataclass
class BehaviorInput:
    pos: np.ndarray
    path: list
    socket: np.ndarray
    battery: float

@dataclasses.dataclass
class BehaviorOutput:
    action: np.ndarray


@irsim.lib.register_behavior("diff", "bscript_behavior")
def call_behavior(ego_object, **kwargs):
    """beahvior module"""
    global battery

    # prepare input and output
    ctx = bscript.context()
    ctx.reset_inactive_states()

    path = [p.state for p in kwargs.get("external_objects", [])]
    ctx.input = BehaviorInput(ego_object.state, path ,socket, battery)

    ctx.output = BehaviorOutput(np.array([[0], [0]]))

    # call bscript behavior
    if battery > 0:
        root_behavior()

    # simulate battery
    dist_to_socket, _ = relative_position(ego_object.state, socket)
    if dist_to_socket < 0.2:
        battery += 5
    else:
        battery -= 0.5

    return ctx.output.action

def main():
    """sim loop"""
    env = irsim.make("world.yaml")

    try:
        for _ in range(1000):
            env.step()
            env.render()
            # depict socket
            env.draw_points([[5, 5]])

            if env.done(): break
    except KeyboardInterrupt:
        pass

    env.end()

if __name__ == "__main__":
    main()
