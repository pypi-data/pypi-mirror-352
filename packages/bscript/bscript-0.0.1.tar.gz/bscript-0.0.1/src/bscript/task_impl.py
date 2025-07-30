from inspect import getcallargs, getgeneratorlocals, isfunction, isgeneratorfunction

from .context_impl import context
from .utils import optional_arg_decorator

class TaskContext:
    def __init__(self, generatorfunction, reset_after_inactivity=False):
        assert isgeneratorfunction(generatorfunction)
        self.generatorfunction = generatorfunction
        self.reset_after_inactivity = reset_after_inactivity
        self.reset()

    def __iter__(self):
        while True:
            try:
                yield self.__call__(supress_stop_iteration=False)
            except StopIteration:
                break

    def reset(self):
        context().reset(self)

    def __call__(self, *args, supress_stop_iteration=True, **kwargs):
        context()._reset_after_inactivity(self)
        callargs = getcallargs(self.generatorfunction, *args, **kwargs)

        # get generator
        default = lambda: self.generatorfunction(**callargs)
        generator = context()._get_state(self, default)

        # update parameter
        getgeneratorlocals(generator).update(callargs)

        # call
        try:
            return next(generator)
        except StopIteration as stop:
            self.reset()
            if supress_stop_iteration:
                return stop.value
            else:
                raise
        except Exception:
            self.reset()
            raise

@optional_arg_decorator
def task(f, reset_after_inactivity=False):
    if isgeneratorfunction(f):
        return TaskContext(f, reset_after_inactivity)
    else:
        assert isfunction(f)
        return f
