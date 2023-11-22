class BusVoltageError(Exception):
    """Exception raised when bus voltage is not set properly."""

    def __init__(self, message="Bus voltage is not set"):
        self.message = message
        super().__init__(self.message)
