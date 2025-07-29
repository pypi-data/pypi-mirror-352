"""Base classes for the DOF robotics framework."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .exceptions import ValidationError


class BaseAction(ABC):
    """Abstract base class for all robotic actions."""

    def __init__(self, name: str, **kwargs):
        """Initialize the action with a name and parameters.

        Args:
            name: Human-readable name for the action
            **kwargs: Action-specific parameters
        """
        self.name = name
        self.parameters = kwargs
        self.validate()

    @abstractmethod
    def execute(self, executor: "BaseExecutor") -> Any:
        """Execute the action using the provided executor.

        Args:
            executor: The executor to run this action

        Returns:
            The result of the action execution
        """
        pass

    def validate(self) -> None:
        """Validate action parameters. Override in subclasses for custom validation.

        Raises:
            ValidationError: If parameters are invalid
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', parameters={self.parameters})"


class BaseExecutor(ABC):
    """Abstract base class for action executors."""

    def __init__(self, name: str = "default"):
        """Initialize the executor.

        Args:
            name: Name identifier for this executor
        """
        self.name = name
        self._connected = False

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the robot/system."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the robot/system."""
        pass

    @property
    def is_connected(self) -> bool:
        """Check if executor is connected."""
        return self._connected

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
