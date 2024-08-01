import traceback


class CException:

    def __init__(self, parent_name: str, function_name: str, exception: Exception):
        self.parent_name = parent_name
        self.function_name: str = function_name
        self.exception = exception
        self.traceback_list: list[str] = traceback.format_exception(
            type(self.exception),
            value=self.exception,
            tb=self.exception.__traceback__)
        self.additional_info: str = ""

    def traceback_short(self) -> str:
        return "".join(self.traceback_list[-2:len(self.traceback_list)])

    def traceback(self) -> str:
        return "".join(self.traceback_list)

    def set_additional_info(self, additional_info: str):
        self.additional_info = additional_info
