"""Skippable sequential agent implementation.

This module provides a sequential agent that can skip remaining sub_agents
at any point during execution.
"""

from __future__ import annotations

from typing import AsyncGenerator, List, Optional

from typing_extensions import override

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.events.event import Event


class SkippableSequentialAgent(BaseAgent):
    """A sequential agent that can skip remaining sub-agents at any point.

    This agent extends the functionality of SequentialAgent by allowing the execution
    to be interrupted and remaining sub-agents to be skipped at any time during the
    execution flow.
    """

    name: str = "skippable_sequential_agent"
    sub_agents: List[BaseAgent] = []
    _skip_remaining: bool = False

    def __init__(self, sub_agents: Optional[List[BaseAgent]] = None):
        """Initialize a new skippable sequential agent.

        Args:
            sub_agents: Optional list of agents to execute in sequence.
        """
        super().__init__()
        if sub_agents is not None:
            self.sub_agents = sub_agents

    def skip_remaining_agents(self) -> str:
        """Signal that remaining sub-agents should be skipped.

        This function can be called by any sub-agent to indicate that
        further processing by subsequent sub-agents is not needed.

        Returns:
            String confirmation that agents will be skipped.
        """
        self._skip_remaining = True
        return "Skipping remaining agents."

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Implementation for async execution of the sequential agent.

        Args:
            ctx: The invocation context of the agent.

        Yields:
            Events from the sub-agents.
        """
        self._skip_remaining = False  # Reset the flag at the start

        for i, sub_agent in enumerate(self.sub_agents):
            if self._skip_remaining:
                # If skip flag is set, stop processing further agents
                break

            # Run the current sub-agent
            async for event in sub_agent.run_async(ctx):
                yield event

            # Check if we should skip after each sub-agent completes
            if self._skip_remaining:
                break

    @override
    async def _run_live_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Implementation for live execution of the sequential agent.

        In live mode, we need to provide sub-agents with the ability to signal
        both task completion and skipping remaining agents.

        Args:
            ctx: The invocation context of the agent.

        Yields:
            Events from the sub-agents.
        """
        self._skip_remaining = False  # Reset the flag at the start

        # Add tool functions to each LlmAgent
        for sub_agent in self.sub_agents:
            if isinstance(sub_agent, LlmAgent):
                # Add task completion function for standard behavior
                def task_completed():
                    """
                    Signals that the model has successfully completed the user's task.
                    """
                    return "Task completion signaled."

                # Add skip function for skipping remaining sub-agents
                def skip_remaining():
                    """
                    Signals that all remaining agents should be skipped.
                    """
                    self._skip_remaining = True
                    return "Skipping all remaining agents."

                # Use function name to dedupe
                if task_completed.__name__ not in sub_agent.tools:
                    sub_agent.tools.append(task_completed)

                if skip_remaining.__name__ not in sub_agent.tools:
                    sub_agent.tools.append(skip_remaining)

                # Update agent instructions for these new functions
                sub_agent.instruction += f"""
                If you finished the user's request according to its description, call the {task_completed.__name__} function
                to exit so the next agents can take over.

                If you determine that ALL remaining agents should be skipped (no further processing is needed),
                call the {skip_remaining.__name__} function.

                When calling either of these functions, do not generate any text other than the function call.
                """

        # Execute sub-agents with skip capability
        for i, sub_agent in enumerate(self.sub_agents):
            if self._skip_remaining:
                # Skip remaining agents if flag is set
                break

            async for event in sub_agent.run_live(ctx):
                yield event

            if self._skip_remaining:
                # Check again after each agent completes
                break
