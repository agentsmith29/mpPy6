import logging

from cmp import CProcessControl as CProcessControl


class CResultRecord:

    def __init__(self, function_name: str, signal_name: str, result):
        self.function_name: str = function_name
        self.signal_name: str = signal_name
        self.result = result

    def emit_signal(self, class_object: CProcessControl):
        if hasattr(class_object, '_module_logger'):
            logger: logging.Logger =  class_object._module_logger
        else:
            logger = logging.getLogger(f"{__name__} - fallback")

        if self.signal_name is None:
            logger.debug(f"Function {self.function_name} returned {self.result}. "
                                               f"No signal to emit.")
            return
        if hasattr(class_object, '_module_logger'):
            logger.debug(f"Function {self.function_name} returned {self.result}. "
                                               f"Emitting {self} in {class_object.__class__.__name__}.")
        emitter = getattr(class_object, self.signal_name).emit
        if isinstance(self.result, tuple):
            emitter(*self.result)
        elif self.result is None:
            emitter()
        else:
            emitter(self.result)


    def __repr__(self):
        if isinstance(self.result, tuple):
            args_str = ', '.join(map(repr, self.result))
        else:
            args_str = repr(self.result)
        # shorten arg_str if too long
        if len(args_str) > 100:
            args_str = args_str[0:10] + '...' + args_str[-10:]
        return f"Signal {self.signal_name}({args_str})"
