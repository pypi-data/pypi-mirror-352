"""
Tests for the qranalyze package.
"""

import sys
import os

# Add the src directory to the path so we can import qranalyze
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import qranalyze
from qranalyze.core import QRAnalyzer


def test_package_import():
    """Test that the package can be imported."""
    assert qranalyze is not None
    print("✓ Package import test passed")


def test_version():
    """Test that the version is accessible."""
    assert hasattr(qranalyze, '__version__')
    assert qranalyze.__version__ == "0.1.0"
    print("✓ Version test passed")


def test_hello_function():
    """Test the hello function."""
    result = qranalyze.hello_qranalyze()
    assert isinstance(result, str)
    assert "QRAnalyze" in result
    print("✓ Hello function test passed")


def test_qr_analyzer_class():
    """Test the QRAnalyzer class."""
    analyzer = QRAnalyzer()
    assert analyzer.version == "0.1.0"
    
    # Test the analyze method
    result = analyzer.analyze("test_data")
    assert isinstance(result, dict)
    assert "status" in result
    assert result["data"] == "test_data"
    print("✓ QRAnalyzer class test passed")


def run_all_tests():
    """Run all tests."""
    print("Running qranalyze tests...")
    print()
    
    test_package_import()
    test_version()
    test_hello_function()
    test_qr_analyzer_class()
    
    print()
    print("All tests passed! ✓")


if __name__ == "__main__":
    run_all_tests() 