"""Robot factory class for creating actions."""

from typing import Union, Optional
from .movement import MoveToAction
from .manipulation import GraspAction, ReleaseAction


class Robot:
    """Factory class for creating robotic actions."""

    @staticmethod
    def move_to(target: Union[str, dict], **kwargs) -> MoveToAction:
        """Create a move-to action.

        Args:
            target: Target location (string name or coordinate dict)
            **kwargs: Additional movement parameters

        Returns:
            MoveToAction instance
        """
        return MoveToAction(target=target, **kwargs)

    @staticmethod
    def grasp(force: Optional[float] = None, **kwargs) -> GraspAction:
        """Create a grasp action.

        Args:
            force: Grasping force (optional)
            **kwargs: Additional grasp parameters

        Returns:
            GraspAction instance
        """
        return GraspAction(force=force, **kwargs)

    @staticmethod
    def release(**kwargs) -> ReleaseAction:
        """Create a release action.

        Args:
            **kwargs: Additional release parameters

        Returns:
            ReleaseAction instance
        """
        return ReleaseAction(**kwargs)
