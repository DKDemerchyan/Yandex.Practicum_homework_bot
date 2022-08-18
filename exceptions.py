class RequestError(Exception):
    pass


class StatusAPIError(Exception):
    pass


class ResponseFormatError(Exception):
    pass


class NoHomeworkError(Exception):
    pass


class HomeworkNotDict(Exception):
    pass


class WrongHomeworkStatusError(Exception):
    pass