import numpy as np
from irsim.util import util
from bscript import Running, input, output

def target_to_action(target):
    _, radian = util.relative_position(input().pos, target)
    diff_radian = util.WrapToPi(radian - input().pos[2, 0])
    return [[np.cos(diff_radian)], [np.sign(diff_radian)]]

def target_reached(target):
    dist, _ = util.relative_position(input().pos, target)
    return dist < 0.2

def drive_to(target):
    if not target_reached(target):
        output().action = target_to_action(target)
        return Running
