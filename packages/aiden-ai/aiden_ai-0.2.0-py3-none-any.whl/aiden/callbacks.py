"""
Callbacks for model building process in Aiden.

This module defines callback interfaces that let users hook into various stages
of the model building process, allowing for custom logging, tracking, visualization,
or other operations to be performed at key points.
"""

import logging
from abc import ABC
from dataclasses import dataclass
from typing import Optional, List

from aiden.common.dataset import Dataset
from aiden.entities.node import Node
from aiden.common.utils.cot.callable import ChainOfThoughtCallable
from aiden.common.utils.cot.emitters import ConsoleEmitter

logger = logging.getLogger(__name__)


@dataclass
class BuildStateInfo:
    """
    Consolidated information about model build state at any point in the process.

    This class combines all information available during different stages of the model building
    process (start, end, iteration start, iteration end) into a single structure.
    """

    # Common identification fields
    intent: str
    """The natural language description of the model's intent."""

    provider: str
    """The provider (LLM) used for generating the model."""

    max_iterations: Optional[int] = None
    """Maximum number of iterations for the model building process."""

    timeout: Optional[int] = None
    """Maximum total time in seconds for the entire model building process."""

    # Iteration fields
    iteration: int = 0
    """Current iteration number (0-indexed)."""

    # Dataset fields
    input_datasets: Optional[List[Dataset]] = None
    """The input datasets."""

    output_dataset: Optional[Dataset] = None
    """The output dataset."""

    # Current node being evaluated
    node: Optional[Node] = None
    """The solution node being evaluated in the current iteration."""


class Callback(ABC):
    """
    Abstract base class for callbacks during model building.

    Callbacks allow running custom code at various stages of the model building process.
    Subclass this and implement the methods you need for your specific use case.
    """

    def on_build_start(self, info: BuildStateInfo) -> None:
        """
        Called when the model building process starts.
        """
        pass

    def on_build_end(self, info: BuildStateInfo) -> None:
        """
        Called when the model building process ends.
        """
        pass

    def on_iteration_start(self, info: BuildStateInfo) -> None:
        """
        Called at the start of each model building iteration.
        """
        pass

    def on_iteration_end(self, info: BuildStateInfo) -> None:
        """
        Called at the end of each model building iteration.
        """
        pass


class ChainOfThoughtModelCallback(Callback):
    """
    Callback that captures and formats the chain of thought for model building.

    This callback bridges between the Aiden callback system and the
    chain of thought callback system.
    """

    def __init__(self, emitter=None):
        """
        Initialize the chain of thought model callback.

        Args:
            emitter: The emitter to use for chain of thought output
        """

        self.cot_callable = ChainOfThoughtCallable(emitter=emitter or ConsoleEmitter())

    def on_build_start(self, info: BuildStateInfo) -> None:
        """
        Reset the chain of thought at the beginning of the build process.
        """
        self.cot_callable.clear()
        self.cot_callable.emitter.emit_thought("System", f"🚀 Starting model build for intent: {info.intent[:40]}...")

    def on_build_end(self, info: BuildStateInfo) -> None:
        """
        Emit completion message at the end of the build process.
        """
        self.cot_callable.emitter.emit_thought("System", "✅ Model build completed")

    def on_iteration_start(self, info: BuildStateInfo) -> None:
        """
        Emit iteration start message.
        """
        self.cot_callable.emitter.emit_thought("System", f"📊 Starting iteration {info.iteration + 1}")

    def on_iteration_end(self, info: BuildStateInfo) -> None:
        """
        Emit iteration end message with performance metrics.
        """
        if info.node:
            self.cot_callable.emitter.emit_thought(
                "System",
                f"📋 Iteration {info.iteration + 1} completed.",
            )
        else:
            self.cot_callable.emitter.emit_thought(
                "System", f"📋 Iteration {info.iteration + 1} failed: No performance metrics available"
            )

    def get_chain_of_thought_callable(self):
        """
        Get the underlying chain of thought callable.

        Returns:
            The chain of thought callable used by this model callback
        """
        return self.cot_callable

    def get_full_chain_of_thought(self) -> List:
        """
        Get the full chain of thought captured during model building.

        Returns:
            The list of steps in the chain of thought
        """
        return self.cot_callable.get_full_chain_of_thought()
