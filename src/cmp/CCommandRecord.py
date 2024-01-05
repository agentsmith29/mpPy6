from cmp import CProcess as CProcess


class CCommandRecord:
    def __init__(self, proc_name: str, func_name: str, *args: (), **kwargs: {}, ):
        self.func_name: str = func_name
        self.args: () = args
        self.kwargs: {} = kwargs
        self.proc_name = proc_name

        self.signal_name: str = None

    def register_signal(self, signal_name: str):
        self.signal_name: str = signal_name

    def execute(self, class_object: CProcess):
        if hasattr(class_object, '_internal_logger'):
            class_object._module_logger.info(f"Executing {self} in {class_object.name}.")
        if self.signal_name is not None:
            getattr(class_object, self.func_name)(signal_name=self.signal_name, *self.args, **self.kwargs)
        else:
            getattr(class_object, self.func_name)(*self.args, **self.kwargs)

    def __repr__(self):
        args_str = ', '.join(map(repr, self.args))
        kwargs_str = ', '.join(f"{key}={repr(value)}" for key, value in self.kwargs.items())
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))
        return f"Function <{self.proc_name}>.{self.func_name}({all_args})"
