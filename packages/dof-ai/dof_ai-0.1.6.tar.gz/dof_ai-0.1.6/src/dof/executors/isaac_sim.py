"""Isaac Sim executor for controlling robots in NVIDIA Isaac Sim.

This executor integrates with Isaac Sim running on the same machine or remotely
using the actual Isaac Sim Python APIs for robot control.
"""

import os
import time
from typing import Any, Union, Dict, Optional, List
from ..core.base import BaseExecutor
from ..core.exceptions import ExecutionError


class IsaacSimExecutor(BaseExecutor):
    """Executor that controls robots in NVIDIA Isaac Sim using the Python API.

    This executor connects to Isaac Sim and uses the omni.isaac.core APIs
    to control robots directly within the simulation environment.
    """

    def __init__(
        self,
        name: str = "isaac_sim",
        robot_prim_path: str = "/World/robot",
        headless: bool = False,
        experience_file: Optional[str] = None,
        enable_cameras: bool = False,
        timeout: float = 30.0,
    ):
        """Initialize the Isaac Sim executor.

        Args:
            name: Name identifier for this executor
            robot_prim_path: USD path to the robot in the Isaac Sim scene
            headless: Whether to run Isaac Sim in headless mode
            experience_file: Optional Isaac Sim experience file to load
            enable_cameras: Whether to enable camera rendering
            timeout: Connection timeout in seconds
        """
        super().__init__(name)

        self.robot_prim_path = robot_prim_path
        self.headless = headless
        self.experience_file = experience_file
        self.enable_cameras = enable_cameras
        self.timeout = timeout

        # Isaac Sim components (initialized in connect)
        self.simulation_app = None
        self.world = None
        self.robot = None
        self.robot_articulation = None

        # Robot state tracking
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.is_grasping = False
        self._isaac_initialized = False

        # Named locations for convenience
        self.named_locations = {
            "home": {"x": 0.0, "y": 0.0, "z": 0.5},
            "pickup": {"x": 0.3, "y": 0.2, "z": 0.3},
            "dropoff": {"x": -0.3, "y": 0.2, "z": 0.3},
        }

    def connect(self) -> None:
        """Establish connection to Isaac Sim and initialize the robot."""
        print(f"🔌 Starting Isaac Sim: {self.name}")

        try:
            # Import Isaac Sim modules (must be done after simulation app is created)
            self._start_simulation_app()
            self._initialize_world()
            self._setup_robot()

            self._connected = True
            self._isaac_initialized = True
            print("✓ Isaac Sim connected and robot initialized")

        except Exception as e:
            self._cleanup()
            raise ExecutionError(f"Failed to connect to Isaac Sim: {e}")

    def disconnect(self) -> None:
        """Close connection to Isaac Sim."""
        if self._connected:
            print(f"🔌 Disconnecting from Isaac Sim: {self.name}")
            self._cleanup()
            print("✓ Isaac Sim disconnected")

    def _start_simulation_app(self) -> None:
        """Start the Isaac Sim simulation application."""
        try:
            # Import here to avoid issues if Isaac Sim is not available
            import isaacsim

            # Configure simulation app settings
            launch_config = {
                "headless": self.headless,
                "enable_cameras": self.enable_cameras,
            }

            if self.experience_file:
                launch_config["experience"] = self.experience_file

            # Start Isaac Sim
            self.simulation_app = isaacsim.SimulationApp(launch_config)

        except ImportError as e:
            raise ExecutionError(
                f"Isaac Sim not found. Please ensure Isaac Sim is properly installed and "
                f"Python path is configured correctly. Error: {e}"
            )
        except Exception as e:
            raise ExecutionError(f"Failed to start Isaac Sim application: {e}")

    def _initialize_world(self) -> None:
        """Initialize the Isaac Sim world and physics context."""
        try:
            # Import Isaac Sim core modules
            from isaacsim.core.api.world import World
            from isaacsim.core.api.simulation_context import SimulationContext

            # Create world with physics
            self.world = World(stage_units_in_meters=1.0)

            # Add default ground plane if it doesn't exist
            self.world.scene.add_default_ground_plane()

            print("✓ Isaac Sim world initialized")

        except Exception as e:
            raise ExecutionError(f"Failed to initialize Isaac Sim world: {e}")

    def _setup_robot(self) -> None:
        """Set up the robot articulation in Isaac Sim."""
        try:
            # Import Isaac Sim robot modules
            from isaacsim.core.prims import SingleArticulation
            from isaacsim.core.utils.stage import get_stage_units

            # Check if robot exists in the scene
            stage = self.world.stage
            if not stage.GetPrimAtPath(self.robot_prim_path):
                print(f"⚠️  Robot not found at {self.robot_prim_path}")
                print("You need to load a robot into the Isaac Sim scene first.")
                print("Try using: Isaac Create Menu > Environments or importing a URDF")
                raise ExecutionError(f"Robot prim not found at {self.robot_prim_path}")

            # Create robot articulation
            self.robot_articulation = SingleArticulation(
                prim_path=self.robot_prim_path, name="robot"
            )

            # Add robot to the world scene
            self.world.scene.add(self.robot_articulation)

            # Reset world to initialize physics
            self.world.reset()

            # Get initial robot position
            position, _ = self.robot_articulation.get_world_pose()
            self.position = {
                "x": float(position[0]),
                "y": float(position[1]),
                "z": float(position[2]),
            }

            print(f"✓ Robot initialized at {self.robot_prim_path}")

        except Exception as e:
            raise ExecutionError(f"Failed to set up robot: {e}")

    def _cleanup(self) -> None:
        """Clean up Isaac Sim resources."""
        try:
            if self.world is not None:
                self.world.clear_instance()
                self.world = None

            if self.simulation_app is not None:
                self.simulation_app.close()
                self.simulation_app = None

        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
        finally:
            self._connected = False
            self._isaac_initialized = False
            self.robot_articulation = None

    def move_to(
        self,
        target: Union[str, Dict],
        speed: str = "normal",
        precision: str = "standard",
    ) -> str:
        """Move robot to target location in Isaac Sim.

        Args:
            target: Target location (coordinates dict or named location)
            speed: Movement speed (slow, normal, fast)
            precision: Movement precision (low, standard, high)

        Returns:
            Status message
        """
        if not self._isaac_initialized:
            raise ExecutionError("Isaac Sim not initialized. Call connect() first.")

        print(f"🎯 Moving robot to {target} in Isaac Sim...")

        try:
            # Resolve target coordinates
            if isinstance(target, str):
                target_coords = self._resolve_named_location(target)
            else:
                target_coords = target

            # Convert to Isaac Sim format (numpy array)
            import numpy as np

            position = np.array(
                [target_coords["x"], target_coords["y"], target_coords["z"]]
            )

            # Set robot position (this is simplified - in practice you'd use motion planning)
            self.robot_articulation.set_world_pose(position=position)

            # Step simulation to apply changes
            for _ in range(10):  # Multiple steps to settle
                self.world.step(render=True)

            # Update position tracking
            self.position.update(target_coords)

            result = f"Moved robot to {target} (speed: {speed}, precision: {precision})"
            print(f"✓ {result}")
            return result

        except Exception as e:
            raise ExecutionError(f"Failed to move robot: {e}")

    def grasp(self, force: Optional[float] = None) -> str:
        """Command robot to grasp an object in Isaac Sim.

        Args:
            force: Grasping force (currently not implemented in this simplified version)

        Returns:
            Status message
        """
        if not self._isaac_initialized:
            raise ExecutionError("Isaac Sim not initialized. Call connect() first.")

        print("🤏 Commanding robot to grasp object in Isaac Sim...")

        try:
            # This is a simplified implementation
            # In practice, you'd control specific gripper joints

            # Get current joint positions
            joint_positions = self.robot_articulation.get_joint_positions()

            # Assume last two joints are gripper (adjust based on your robot)
            if len(joint_positions) >= 2:
                # Close gripper (set small positive values)
                joint_positions[-2:] = [0.02, 0.02]  # Closed position
                self.robot_articulation.set_joint_positions(joint_positions)

                # Step simulation
                for _ in range(10):
                    self.world.step(render=True)

            self.is_grasping = True
            force_str = f" with force {force}" if force is not None else ""
            result = f"Robot grasped object{force_str}"

            print(f"✓ {result}")
            return result

        except Exception as e:
            raise ExecutionError(f"Failed to grasp: {e}")

    def release(self) -> str:
        """Command robot to release a grasped object in Isaac Sim.

        Returns:
            Status message
        """
        if not self._isaac_initialized:
            raise ExecutionError("Isaac Sim not initialized. Call connect() first.")

        print("🤲 Commanding robot to release object in Isaac Sim...")

        try:
            # Get current joint positions
            joint_positions = self.robot_articulation.get_joint_positions()

            # Assume last two joints are gripper (adjust based on your robot)
            if len(joint_positions) >= 2:
                # Open gripper (set larger positive values)
                joint_positions[-2:] = [0.08, 0.08]  # Open position
                self.robot_articulation.set_joint_positions(joint_positions)

                # Step simulation
                for _ in range(10):
                    self.world.step(render=True)

            self.is_grasping = False
            result = "Robot released object"

            print(f"✓ {result}")
            return result

        except Exception as e:
            raise ExecutionError(f"Failed to release: {e}")

    def _resolve_named_location(self, location_name: str) -> Dict[str, float]:
        """Resolve a named location to coordinates.

        Args:
            location_name: Name of the location

        Returns:
            Coordinate dictionary
        """
        if location_name in self.named_locations:
            return self.named_locations[location_name]
        else:
            raise ExecutionError(f"Unknown named location: {location_name}")

    def get_robot_status(self) -> Dict[str, Any]:
        """Get current robot status from Isaac Sim.

        Returns:
            Robot status information
        """
        if not self._isaac_initialized:
            return {"error": "Isaac Sim not initialized"}

        try:
            position, orientation = self.robot_articulation.get_world_pose()
            joint_positions = self.robot_articulation.get_joint_positions()
            joint_velocities = self.robot_articulation.get_joint_velocities()

            return {
                "position": {
                    "x": float(position[0]),
                    "y": float(position[1]),
                    "z": float(position[2]),
                },
                "orientation": orientation.tolist()
                if orientation is not None
                else None,
                "joint_positions": joint_positions.tolist()
                if joint_positions is not None
                else None,
                "joint_velocities": joint_velocities.tolist()
                if joint_velocities is not None
                else None,
                "is_grasping": self.is_grasping,
                "connected": self._connected,
            }

        except Exception as e:
            return {"error": str(e)}

    @property
    def current_position(self) -> Dict[str, float]:
        """Get current robot position."""
        return self.position.copy()

    @property
    def has_object(self) -> bool:
        """Check if robot is currently grasping an object."""
        return self.is_grasping
