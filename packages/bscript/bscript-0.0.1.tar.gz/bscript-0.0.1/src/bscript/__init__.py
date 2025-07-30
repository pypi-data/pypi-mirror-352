from .task_impl import task
from .context_impl import bScriptContext, context, input, output
from .fsm_impl import fsm, initial, NoInitialStateFound, Transition

Running = True
Success = None

class Failure(Exception): pass

__all__ = ["task", "bScriptContext", "context", "input", "output",
           "fsm", "initial", "NoInitialStateFound", "Transition",
           "Running", "Success", "Failure"]
