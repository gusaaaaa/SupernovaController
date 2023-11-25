class DeviceOpenError(Exception):
    """Exception raised when open connection fails."""

    def __init__(self, message="Open connection failed"):
        self.message = message
        super().__init__(self.message)

class DeviceNotMountedError(Exception):
    """Exception raised when trying to execute an operation on an unmounted device."""

    def __init__(self, message="Device not mounted"):
        self.message = message
        super().__init__(self.message)

class UnknownInterfaceError(Exception):
    """Exception raised when trying to create an unknown interface."""

    def __init__(self, message="Unknown interface name"):
        self.message = message
        super().__init__(self.message)

class BusVoltageError(Exception):
    """Exception raised when bus voltage is not set properly."""

    def __init__(self, message="Bus voltage is not set"):
        self.message = message
        super().__init__(self.message)

class BusNotInitializedError(Exception):
    """Exception raised when bus was not properly initialized."""

    def __init__(self, message="Bus not initialized"):
        self.message = message
        super().__init__(self.message)
