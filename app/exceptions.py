"""Domain exceptions for the Chaos Demo service."""


class OrderProcessingError(Exception):
    """Raised when an order processing failure is simulated."""
    def __init__(self, message: str = "Inventory allocation lock timeout during order checkout"):
        super().__init__(message)
        self.message = message
