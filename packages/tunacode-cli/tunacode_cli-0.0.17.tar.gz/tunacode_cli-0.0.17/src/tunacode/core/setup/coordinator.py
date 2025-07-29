"""Module: tunacode.core.setup.coordinator

Setup orchestration and coordination for the TunaCode CLI.
Manages the execution order and validation of all registered setup steps.
"""

from typing import List

from tunacode.core.setup.base import BaseSetup
from tunacode.core.state import StateManager
from tunacode.ui import console as ui


class SetupCoordinator:
    """Coordinator for running all setup steps in order."""

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.setup_steps: List[BaseSetup] = []

    def register_step(self, step: BaseSetup) -> None:
        """Register a setup step to be run."""
        self.setup_steps.append(step)

    async def run_setup(self, force_setup: bool = False) -> None:
        """Run all registered setup steps in order."""
        for step in self.setup_steps:
            try:
                if await step.should_run(force_setup):
                    # Silent setup - no messages
                    await step.execute(force_setup)

                    if not await step.validate():
                        await ui.error(f"Setup validation failed: {step.name}")
                        raise RuntimeError(
                            f"Setup step '{step.name}' failed validation"
                        )
                else:
                    # Skip silently
                    pass
            except Exception as e:
                await ui.error(f"Setup failed at step '{step.name}': {str(e)}")
                raise

    def clear_steps(self) -> None:
        """Clear all registered setup steps."""
        self.setup_steps.clear()
