"""Custom exceptions for the DOF robotics framework."""


class DOFError(Exception):
    """Base exception for all DOF-related errors."""

    pass


class ExecutionError(DOFError):
    """Raised when an action fails to execute properly."""

    pass


class ValidationError(DOFError):
    """Raised when action parameters are invalid."""

    pass


class ChainError(DOFError):
    """Raised when there's an issue with chain execution."""

    pass


class RobotConnectionError(DOFError):
    """Raised when there's an issue connecting to the robot."""

    pass
