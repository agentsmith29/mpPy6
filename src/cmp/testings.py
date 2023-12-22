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
