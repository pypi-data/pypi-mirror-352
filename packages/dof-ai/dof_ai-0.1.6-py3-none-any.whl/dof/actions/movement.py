"""Movement actions for robotic systems."""

from typing import Any, Union
from ..core.base import BaseAction, BaseExecutor
from ..core.exceptions import ValidationError


class MoveToAction(BaseAction):
    """Action for moving to a specific target."""

    def __init__(self, target: Union[str, dict], **kwargs):
        """Initialize a move-to action.

        Args:
            target: Target location (can be a string name or coordinate dict)
            **kwargs: Additional parameters like speed, precision, etc.
        """
        super().__init__(name=f"move_to_{target}", target=target, **kwargs)

    def validate(self) -> None:
        """Validate movement parameters."""
        target = self.parameters.get("target")
        if not target:
            raise ValidationError("Target is required for move action")

        if isinstance(target, dict):
            # Validate coordinate format if target is a dict
            required_keys = {"x", "y", "z"}
            if not required_keys.issubset(target.keys()):
                raise ValidationError(f"Coordinate target must contain {required_keys}")

    def execute(self, executor: BaseExecutor) -> Any:
        """Execute the movement action."""
        target = self.parameters["target"]
        speed = self.parameters.get("speed", "normal")
        precision = self.parameters.get("precision", "standard")

        # This would interface with the actual robot executor
        return executor.move_to(target, speed=speed, precision=precision)
