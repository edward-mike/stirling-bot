import pytest
import logging
import time
from unittest.mock import patch
from utils import time_execution


@time_execution
def test_function():
    time.sleep(0.1)
    return "success"

@patch("logging.info")
def test_time_execution_decorator(mock_logging_info):
    result = test_function()
    
    assert result == "success"
    # Check if logging.info was called with the expected message format
    assert mock_logging_info.call_count == 1
    log_call_args = mock_logging_info.call_args[0][0]
    assert log_call_args.startswith("Execution time of test_function: ")
    assert " sec." in log_call_args