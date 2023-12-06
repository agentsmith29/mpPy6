import datetime
from functools import wraps

import cmp


class _Cache(object):

    def __init__(self, func, fset, signal_name):
        # Plain function as argument to be decorated
        self.func = func
        self.fset = fset
        self.signal_name = signal_name

    def __get__(self, instance, owner):
        self.instance_ = instance
        return self.__call__

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        print(f"Setting {obj}, {value}!")
        self.fset(obj, value)

    @staticmethod
    def set(signal_name):
        print("************ 1 Setting!")

    def __call__(self, *args, **kwargs):
        """Invoked on every call of decorated method"""

        # set attribute on instance
        name = '%s_called' % self.func.__name__
        # print(f"Setting {name} in {}!")
        self.instance_._internal_logger.debug(
            f"Setting {name} in {self.instance_.__class__.__name__} and emitting {self.signal_name}!")
        # setattr(self.instance_, name, datetime.utcnow())

        # returning original function with class' instance as self
        return self.func(self.instance_, *args, **kwargs)


# wrap _Cache to allow for deferred calling
def Cache(function=None, signal_name=None):
    if function:
        return _Cache(function)
    else:
        def wrapper(function):
            return _Cache(function, signal_name)

        return wrapper


class CProperty:
    def __init__(self, fget = None, fset=None, emit_to: str = None):
        self.fget = fget
        self.fset = fset
        self.signal_name = emit_to
        self.instance_ = None

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj: cmp.CProcess, value):

        if self.fset is None:
            raise AttributeError("can't set attribute")

        obj._internal_logger.debug(f"Setting {self.signal_name}!")
        result = cmp.CResultRecord(str(self.fset.__name__), self.signal_name, value)
        obj.state_queue.put(result)

        self.fset(obj, value)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.signal_name)

    def _setter(self, fset):
        return type(self)(self.fget, fset, self.signal_name)

    def setter(self, emit_to: str):
        return type(self)(self.fget, self.fset, emit_to=emit_to)._setter


