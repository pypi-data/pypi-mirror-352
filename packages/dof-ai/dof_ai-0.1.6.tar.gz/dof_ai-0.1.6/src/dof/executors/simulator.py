"""Simulator executor for testing and development."""

import time
from typing import Any, Union, Dict, Optional, Mapping
from ..core.base import BaseExecutor


class SimulatorExecutor(BaseExecutor):
    """Executor that simulates robot operations for testing and development."""

    def __init__(self, name: str = "simulator", simulation_delay: float = 0.5):
        """Initialize the simulator executor.

        Args:
            name: Name identifier for this executor
            simulation_delay: Delay in seconds to simulate operation time
        """
        super().__init__(name)
        self.simulation_delay = simulation_delay
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.is_grasping = False

    def connect(self) -> None:
        """Simulate connection to robot."""
        print(f"🔌 Connecting to simulator: {self.name}")
        time.sleep(self.simulation_delay / 2)
        self._connected = True
        print("✓ Simulator ready")

    def disconnect(self) -> None:
        """Simulate disconnection from robot."""
        if self._connected:
            print(f"🔌 Disconnecting from simulator: {self.name}")
            self._connected = False
            print("✓ Simulator disconnected")

    def move_to(
        self,
        target: Union[str, Dict],
        speed: str = "normal",
        precision: str = "standard",
    ) -> str:
        """Simulate movement to target location.

        Args:
            target: Target location
            speed: Movement speed
            precision: Movement precision

        Returns:
            Status message
        """
        print(f"🎯 Moving to {target}...")

        # Simulate movement delay based on speed
        speed_multiplier = {"slow": 2.0, "normal": 1.0, "fast": 0.5}.get(speed, 1.0)
        time.sleep(self.simulation_delay * speed_multiplier)

        # Update simulated position
        if isinstance(target, dict) and "x" in target:
            self.position.update(target)

        result = f"Moved to {target} (speed: {speed}, precision: {precision})"
        print(f"✓ {result}")
        return result

    def grasp(self, force: Optional[float] = None) -> str:
        """Simulate grasping an object.

        Args:
            force: Grasping force

        Returns:
            Status message
        """
        print("🤏 Grasping object...")
        time.sleep(self.simulation_delay)

        self.is_grasping = True
        force_str = f" with force {force}" if force is not None else ""
        result = f"Grasped object{force_str}"

        print(f"✓ {result}")
        return result

    def release(self) -> str:
        """Simulate releasing a grasped object.

        Returns:
            Status message
        """
        print("🤲 Releasing object...")
        time.sleep(self.simulation_delay)

        self.is_grasping = False
        result = "Released object"

        print(f"✓ {result}")
        return result

    @property
    def current_position(self) -> Dict[str, float]:
        """Get current simulated position."""
        return self.position.copy()

    @property
    def has_object(self) -> bool:
        """Check if simulator is currently grasping an object."""
        return self.is_grasping
