from time import sleep
from random import random

from bscript import task, Running, Failure

##### actions #####
@task
def peel_banana():
    if random() < 0.3:
        print("peeling banana failed"); raise Failure()
    print("peeling banana"); yield Running
    # implicit return None / return Success

@task
def eat_apple():
    print("eating apple"); yield Running

@task
def eat_banana():
    if random() < 0.3:
        print("eating banana failed"); raise Failure()
    print("eating banana"); yield Running

def listen_to_the_radio():
    print("~lalala~"); return Running

def handle_emergency():
    print("running"); return Running

##### conditions #####
@task
def emergency():
    if random() > 0.9:
        print("!fire!"); yield Running
        print("!fire!"); yield Running

##### composites #####
def eat_something():
    # a (behavior tree) decorator
    if emergency():
        return handle_emergency()
    else:
        return eat() and listen_to_the_radio()

@task
def eat():
    # a (behavior tree) fallback
    try:
        while consume_banana(): yield Running
    except Failure:
        while eat_apple(): yield Running

@task
def consume_banana():
    # a (behavior tree) sequence
    while peel_banana(): yield Running
    while eat_banana(): yield Running

##### main loop #####
for _ in range(20):
    print(eat_something())
    sleep(1)
    print("-----frame-----")
