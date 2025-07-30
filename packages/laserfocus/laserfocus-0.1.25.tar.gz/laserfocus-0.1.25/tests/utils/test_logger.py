import pytest
from unittest.mock import patch, MagicMock
from laserfocus.utils.logger import Logger

@pytest.fixture
def logger():
    return Logger()

def test_logger_initialization(logger):
    assert logger.console is not None
    assert logger.logger is not None

@patch('logging.Logger.debug')
def test_logger_info(mock_debug, logger):
    test_message = "test info message"
    logger.info(test_message)
    mock_debug.assert_called_once_with(
        f"[blue]{test_message}[/blue]",
        extra={'markup': True}
    )

@patch('logging.Logger.debug')
def test_logger_success(mock_debug, logger):
    test_message = "test success message"
    logger.success(test_message)
    mock_debug.assert_called_once_with(
        f"[green]{test_message}[/green]",
        extra={'markup': True}
    )

@patch('logging.Logger.info')
def test_logger_announcement_info(mock_info, logger):
    test_message = "test announcement"
    logger.announcement(test_message, type='info')
    mock_info.assert_called_once_with(
        f"[red bold]{test_message}[/red bold]",
        extra={'markup': True}
    )

@patch('logging.Logger.info')
def test_logger_announcement_success(mock_info, logger):
    test_message = "test announcement"
    logger.announcement(test_message, type='success')
    mock_info.assert_called_once_with(
        f"[white bold]{test_message}[/white bold]\n",
        extra={'markup': True}
    )

def test_logger_announcement_invalid_type(logger):
    with pytest.raises(ValueError, match="Invalid type. Choose 'info' or 'success'."):
        logger.announcement("test", type='invalid')

@patch('logging.Logger.warning')
def test_logger_warning(mock_warning, logger):
    test_message = "test warning message"
    logger.warning(test_message)
    mock_warning.assert_called_once_with(
        f"[yellow bold on white]{test_message}[/yellow bold on white]",
        extra={'markup': True}
    )

@patch('logging.Logger.error')
def test_logger_error(mock_error, logger):
    test_message = "test error message"
    logger.error(test_message)
    mock_error.assert_called_once_with(
        f"[red bold on white]{test_message}[/red bold on white]",
        extra={'markup': True}
    ) 