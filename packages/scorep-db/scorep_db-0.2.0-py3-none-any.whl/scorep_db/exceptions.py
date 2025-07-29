class IllFormedQueryError(Exception):
    """IllFormedQueryError is raised if a query does not contain the needed results"""

    def __init__(self, message, code=""):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f"IllFormedQueryError [Code {self.code}]: {self.message}"


class ConfigError(Exception):
    pass
