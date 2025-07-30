from behavior_utils import drive_to, target_reached
from bscript import Running, Success, Transition, input, initial, fsm

@fsm
class follow_path:
    idx = 0

    @initial
    def follow(self):
        if target_reached(input().path[self.idx]):
            self.idx = (self.idx + 1) % len(input().path)

        return drive_to(input().path[self.idx])

@fsm
class charging:
    @initial
    def charged(self):
        if input().battery < 25:
            return Transition(self.driveToSocket)

    def driveToSocket(self):
        if drive_to(input().socket) == Success:
            return Transition(self.recharge)
        return Running

    def recharge(self):
        if input().battery >= 100:
            return Transition(self.charged)
        return Running

def root_behavior():
    if not charging(): follow_path()
