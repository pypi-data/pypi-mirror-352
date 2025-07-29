"""Tests for groundit core functionality."""

import pytest
from groundit.core import greet, get_version


def test_greet():
    """Test the greet function."""
    result = greet("World")
    assert result == "Hello World, welcome to groundit!"


def test_get_version():
    """Test the get_version function."""
    version = get_version()
    assert version == "0.1.0" 