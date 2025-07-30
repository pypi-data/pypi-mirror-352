class NoCompanyError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class NoDataError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class NotSupportedError(Exception):
    def __init__(self, msg):
        super().__init__(msg)