"""
Test for the hello function in recallkit.
"""
from recallkit import hello


def test_hello():
    """Test that the hello function returns the expected greeting."""
    assert hello() == "Hello from recallkit!"
    print("Hello world test passed!")
