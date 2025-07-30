"""
Tests for the MemoryFilter class in recallkit.memory_filter.
"""
import pytest
from litellm import AllMessageValues

from recallkit.memory_filter import MemoryFilter
from recallkit.util.messages import user_message


def test_filter_relevant_memories(completion_model):
    """
    Test that the filter_relevant_memories method correctly processes the response
    and returns the expected relevance list.
    """
    # Create a MemoryFilter instance with the fixture
    memory_filter = MemoryFilter(completion_model)

    # Sample messages and memories
    messages = user_message("Tell me about Python programming")
    memories = [
        "Python is a high-level programming language.",
        "My dog is very friendly.",
        "Python has libraries like NumPy and Pandas for data analysis."
    ]

    # Call the method with real model
    result = memory_filter.filter_relevant_memories([messages], memories)

    assert result == [True, False, True]
