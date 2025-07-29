"""Manipulation actions for robotic systems."""

from typing import Any, Optional
from ..core.base import BaseAction, BaseExecutor
from ..core.exceptions import ValidationError


class GraspAction(BaseAction):
    """Action for grasping an object."""

    def __init__(self, force: Optional[float] = None, **kwargs):
        """Initialize a grasp action.

        Args:
            force: Grasping force (optional)
            **kwargs: Additional parameters
        """
        super().__init__(name="grasp", force=force, **kwargs)

    def validate(self) -> None:
        """Validate grasp parameters."""
        force = self.parameters.get("force")
        if force is not None and (not isinstance(force, (int, float)) or force < 0):
            raise ValidationError("Force must be a non-negative number")

    def execute(self, executor: BaseExecutor) -> Any:
        """Execute the grasp action."""
        force = self.parameters.get("force")
        return getattr(
            executor, "grasp", lambda **kw: f"Simulated grasp with force={force}"
        )(force=force)


class ReleaseAction(BaseAction):
    """Action for releasing a grasped object."""

    def __init__(self, **kwargs):
        """Initialize a release action.

        Args:
            **kwargs: Additional parameters
        """
        super().__init__(name="release", **kwargs)

    def execute(self, executor: BaseExecutor) -> Any:
        """Execute the release action."""
        return getattr(executor, "release", lambda **kw: "Simulated release")()
