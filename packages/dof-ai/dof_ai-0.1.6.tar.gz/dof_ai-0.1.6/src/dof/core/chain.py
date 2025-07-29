"""Chain class for sequencing robotic actions."""

from typing import List, Any, Optional, Iterator, Union, overload
from .base import BaseAction, BaseExecutor
from .exceptions import ChainError, ExecutionError


class Chain:
    """A chain of robotic actions that can be executed sequentially."""

    def __init__(self, name: str = "RobotChain", mode: str = "simulator"):
        """Initialize a new chain.

        Args:
            name: Name identifier for this chain
            mode: Execution mode - "simulator", "isaac", or "robot"
        """
        self.name = name
        self.mode = mode
        self.actions: List[BaseAction] = []
        self._results: List[Any] = []

    def add(self, action: BaseAction) -> "Chain":
        """Add an action to the chain.

        Args:
            action: The action to add to the chain

        Returns:
            Self for method chaining
        """
        if not isinstance(action, BaseAction):
            raise ChainError(f"Expected BaseAction, got {type(action)}")

        self.actions.append(action)
        return self

    def _create_default_executor(self) -> BaseExecutor:
        """Create a default executor based on the chain mode.

        Returns:
            The appropriate executor for the current mode
        """
        if self.mode == "isaac":
            # Import here to avoid circular imports
            from ..executors.isaac_sim import IsaacSimExecutor

            return IsaacSimExecutor()
        elif self.mode == "simulator":
            # Import here to avoid circular imports
            from ..executors.simulator import SimulatorExecutor

            return SimulatorExecutor()
        elif self.mode == "robot":
            # Import here to avoid circular imports
            from ..executors.base_robot import BaseRobotExecutor

            # Provide a default robot config - users should pass their own executor for real robots
            default_robot_config = {"type": "generic", "connection": "default"}
            return BaseRobotExecutor(robot_config=default_robot_config)
        else:
            raise ChainError(
                f"Unknown execution mode: {self.mode}. Supported modes: 'simulator', 'isaac', 'robot'"
            )

    @overload
    def execute(self, executor: BaseExecutor) -> List[Any]: ...

    @overload
    def execute(self) -> List[Any]: ...

    def execute(self, executor: Optional[BaseExecutor] = None) -> List[Any]:
        """Execute all actions in the chain sequentially.

        Args:
            executor: The executor to run the actions. If None, creates one based on mode.

        Returns:
            List of results from each action

        Raises:
            ChainError: If chain is empty or execution fails
            ExecutionError: If any action fails to execute
        """
        if not self.actions:
            raise ChainError("Cannot execute empty chain")

        # If no executor provided, create one based on mode
        if executor is None:
            executor = self._create_default_executor()
            should_manage_connection = True
        else:
            should_manage_connection = False

        # Manage connection if we created the executor
        if should_manage_connection:
            print(f"🔧 Using {self.mode} mode with {executor.__class__.__name__}")
            executor.connect()

        if not executor.is_connected:
            raise ChainError("Executor must be connected before execution")

        self._results = []

        try:
            for i, action in enumerate(self.actions):
                try:
                    print(
                        f"Executing action {i + 1}/{len(self.actions)}: {action.name}"
                    )
                    result = action.execute(executor)
                    self._results.append(result)
                    print(f"✓ Action '{action.name}' completed successfully")
                except Exception as e:
                    error_msg = (
                        f"Action '{action.name}' failed at step {i + 1}: {str(e)}"
                    )
                    print(f"✗ {error_msg}")
                    raise ExecutionError(error_msg) from e

            print(
                f"Chain '{self.name}' completed successfully with {len(self.actions)} actions"
            )
        finally:
            # Disconnect if we managed the connection
            if should_manage_connection:
                executor.disconnect()

        return self._results

    def clear(self) -> None:
        """Clear all actions from the chain."""
        self.actions.clear()
        self._results.clear()

    @property
    def length(self) -> int:
        """Get the number of actions in the chain."""
        return len(self.actions)

    @property
    def results(self) -> List[Any]:
        """Get the results from the last execution."""
        return self._results.copy()

    def __len__(self) -> int:
        """Get the number of actions in the chain."""
        return len(self.actions)

    def __iter__(self) -> Iterator[BaseAction]:
        """Iterate over actions in the chain."""
        return iter(self.actions)

    def __repr__(self) -> str:
        return f"Chain(name='{self.name}', mode='{self.mode}', actions={len(self.actions)})"
