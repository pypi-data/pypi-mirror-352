class ZumaExecutionError(Exception):
    """Custom exception to signal Zuma workflow execution failure."""

    def __init__(self, message: str, component_name: str = None, original_error: Exception = None):
        super().__init__(message)
        self.component_name = component_name
        self.original_error = original_error


class ZumaValidationError(Exception):
    """Exception for Zuma workflow validation errors."""

    pass
