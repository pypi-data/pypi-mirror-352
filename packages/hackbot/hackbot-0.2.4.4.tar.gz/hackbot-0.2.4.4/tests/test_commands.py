import pytest
import argparse
import tempfile
import os
import json
from unittest.mock import patch, MagicMock, call
from aiohttp.client_exceptions import ClientPayloadError
from src.hackbot.commands import (
    hackbot_run,
    show_selectable_models,
    check_common_args,
    check_run_args,
    check_scope_args,
    setup_parser,
    check_learn_args,
)
from src.hackbot.hack import HackbotAuthError


@pytest.fixture
def mock_args():
    args = MagicMock()
    args.api_key = "test_api_key"
    args.source = "test_source"
    args.output = None
    args.auth_only = False
    args.issues_repo = None
    args.github_api_key = None
    args.command = "run"
    return args


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.authenticate")
@patch("src.hackbot.commands.cli_run")
@patch("src.hackbot.commands.Path")
def test_hackbot_run_success(mock_path_class, mock_cli_run, mock_auth, mock_exists, mock_args):
    """Test successful hackbot run command execution"""
    # Set up Path mock
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.absolute.return_value = mock_path
    mock_path_class.return_value = mock_path
    mock_path_class.resolve.return_value = mock_path

    mock_exists.return_value = True
    mock_auth.return_value = None  # Success case returns None
    mock_cli_run.return_value = [{"bug_id": "TEST-1"}]

    result = hackbot_run(mock_args)
    assert result == 0

    mock_auth.assert_called_once()
    mock_cli_run.assert_called_once()


@patch("src.hackbot.commands.os.path.exists")
def test_hackbot_run_invalid_source(mock_exists, mock_args):
    """Test hackbot run with invalid source directory"""
    mock_exists.return_value = False

    result = hackbot_run(mock_args)
    assert result == 1


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.authenticate")
def test_hackbot_run_auth_failure(mock_auth, mock_exists, mock_args):
    """Test hackbot run with authentication failure"""
    mock_exists.return_value = True
    mock_auth.return_value = HackbotAuthError(
        "Authentication failed"
    )  # Failure case returns HackbotAuthError

    result = hackbot_run(mock_args)
    assert result == 1


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.authenticate")
@patch("src.hackbot.commands.cli_run")
def test_hackbot_run_auth_only(mock_cli_run, mock_auth, mock_exists, mock_args):
    """Test hackbot run with auth_only flag"""
    mock_exists.return_value = True
    mock_auth.return_value = None  # Success case returns None
    mock_args.auth_only = True

    result = hackbot_run(mock_args)
    assert result == 0

    mock_cli_run.assert_not_called()


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.authenticate")
@patch("src.hackbot.commands.cli_run")
@patch("src.hackbot.commands.Path")
def test_hackbot_run_with_output(
    mock_path_class, mock_cli_run, mock_auth, mock_exists, mock_args, tmp_path
):
    """Test hackbot run with output file"""
    # Set up Path mock
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.absolute.return_value = mock_path
    mock_path_class.return_value = mock_path
    mock_path_class.resolve.return_value = mock_path

    mock_exists.return_value = True
    mock_auth.return_value = None  # Success case returns None
    test_results = [{"bug_id": "TEST-1", "title": "Test Bug", "description": "Test Description"}]
    mock_cli_run.return_value = test_results

    output_file = tmp_path / "output.json"
    mock_args.output = str(output_file)

    result = hackbot_run(mock_args)
    assert result == 0

    assert output_file.exists()
    with open(output_file) as f:
        saved_results = json.load(f)
    assert saved_results == test_results


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.authenticate")
@patch("src.hackbot.commands.cli_run")
@patch("src.hackbot.commands.Path")
def test_hackbot_run_client_payload_error(
    mock_path_class, mock_cli_run, mock_auth, mock_exists, mock_args
):
    """Test hackbot run with ClientPayloadError"""
    # Set up Path mock
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.absolute.return_value = mock_path
    mock_path_class.return_value = mock_path
    mock_path_class.resolve.return_value = mock_path

    mock_exists.return_value = True
    mock_auth.return_value = None  # Success case returns None
    mock_cli_run.side_effect = ClientPayloadError()

    result = hackbot_run(mock_args)
    assert result == 1


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.authenticate")
@patch("src.hackbot.commands.cli_run")
@patch("src.hackbot.commands.Path")
def test_hackbot_run_413_error(mock_path_class, mock_cli_run, mock_auth, mock_exists, mock_args):
    """Test hackbot run with 413 error"""
    # Set up Path mock
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.absolute.return_value = mock_path
    mock_path_class.return_value = mock_path
    mock_path_class.resolve.return_value = mock_path

    mock_exists.return_value = True
    mock_auth.return_value = None  # Success case returns None
    mock_cli_run.side_effect = Exception("Hack request failed: 413")

    result = hackbot_run(mock_args)
    assert result == 1


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.authenticate")
@patch("src.hackbot.commands.cli_run")
@patch("src.hackbot.commands.Path")
def test_hackbot_run_unexpected_error(
    mock_path_class, mock_cli_run, mock_auth, mock_exists, mock_args
):
    """Test hackbot run with unexpected error"""
    # Set up Path mock
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.absolute.return_value = mock_path
    mock_path_class.return_value = mock_path
    mock_path_class.resolve.return_value = mock_path

    mock_exists.return_value = True
    mock_auth.return_value = None  # Success case returns None
    mock_cli_run.side_effect = Exception("Unexpected error")

    with pytest.raises(Exception) as excinfo:
        hackbot_run(mock_args)
    assert str(excinfo.value) == "Unexpected error"


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.Path")
def test_check_api_args(mock_path_class, mock_exists):
    """Test API argument validation"""
    parser = setup_parser()

    # Set up Path mock
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.absolute.return_value = mock_path
    mock_path_class.return_value = mock_path
    mock_path_class.resolve.return_value = mock_path

    # Test without API key
    args = parser.parse_args(["run", "--source", "."])
    args.api_key = None  # Explicitly set API key to None
    mock_exists.return_value = True
    result = check_common_args(args)
    assert result == 1

    # Test with API key and foundry.toml present
    args = parser.parse_args(
        [
            "run",
            "--api-key",
            "test-key",
            "--source",
            ".",
        ]
    )
    mock_exists.return_value = True
    result = check_common_args(args)
    assert isinstance(result, argparse.Namespace)
    assert result.api_key == "test-key"
    assert result.command == "run"


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.Path")
def test_check_scope_args(mock_path_class, mock_exists):
    """Test scope argument validation"""
    parser = setup_parser()

    # Set up Path mock
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.absolute.return_value = mock_path
    mock_path_class.return_value = mock_path
    mock_path_class.resolve.return_value = mock_path

    args = parser.parse_args(
        [
            "scope",
            "--api-key",
            "test-key",
            "--source",
            ".",
        ]
    )

    mock_exists.return_value = True
    result = check_scope_args(args)
    assert isinstance(result, argparse.Namespace)
    assert result.api_key == "test-key"
    assert result.command == "scope"


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.Path")
def test_check_run_args(mock_path_class, mock_exists):
    """Test run command argument validation"""
    parser = setup_parser()

    # Set up Path mock
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.absolute.return_value = mock_path
    mock_path_class.return_value = mock_path
    mock_path_class.resolve.return_value = mock_path

    # Test with foundry.toml present and valid arguments
    args = parser.parse_args(
        [
            "run",
            "--api-key",
            "test-key",
            "--source",
            ".",
        ]
    )
    mock_exists.return_value = True
    result = check_run_args(args)
    assert isinstance(result, argparse.Namespace)
    assert result.api_key == "test-key"
    assert result.command == "run"


def test_check_run_args_foundry():
    """Test run command argument validation"""
    parser = setup_parser()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Resolve the real path to handle symlinks
        tmpdir = os.path.realpath(tmpdir)
        foundry_path = os.path.join(tmpdir, "foundry.toml")
        with open(foundry_path, "w") as f:
            f.write("# Temporary foundry.toml")
            f.flush()

        args = parser.parse_args(
            [
                "run",
                "--api-key",
                "test-key",
                "--source",
                tmpdir,
            ]
        )

        with patch("src.hackbot.commands.os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda x: True if x == foundry_path else False
            result = check_run_args(args)
            assert isinstance(result, argparse.Namespace)
            assert result.command == "run"
            assert result.source == tmpdir


@patch("src.hackbot.commands.get_selectable_models")
@patch("src.hackbot.commands.log.info")
def test_show_selectable_models(mock_logger, mock_get_selectable_models):
    """Test model listing functionality"""
    mock_get_selectable_models.return_value = ["model1", "model2", "model3"]

    result = show_selectable_models(api_key="test-key")
    assert result == 0

    # Verify models were logged, ignoring ANSI color codes
    mock_logger.assert_has_calls(
        [
            call(mock_logger.call_args_list[0][0][0]),  # First call with any string
            call("  - model1"),
            call("  - model2"),
            call("  - model3"),
            call(mock_logger.call_args_list[-1][0][0]),  # Last call with any string
        ],
        any_order=False,
    )


def test_check_learn_args():
    """Test learn command validation"""
    parser = setup_parser()

    # Test without URL
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(
            [
                "learn",
                "--api-key",
                "test-key",
            ]
        )
    assert excinfo.value.code == 2

    # Test without API key
    args = parser.parse_args(
        [
            "learn",
            "--url",
            "https://example.com",
        ]
    )
    args.api_key = None  # Override default value
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        result = check_learn_args(args)
        assert result == 1

    # Test with valid arguments
    args = parser.parse_args(
        [
            "learn",
            "--api-key",
            "test-key",
            "--url",
            "https://example.com",
        ]
    )
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        result = check_learn_args(args)
        assert isinstance(result, argparse.Namespace)
        assert result.api_key == "test-key"
        assert result.command == "learn"
        assert result.url == "https://example.com"

    # Test merge flag with no existing checklist
    args = parser.parse_args(
        [
            "learn",
            "--api-key",
            "test-key",
            "--url",
            "https://example.com",
            "--merge",
        ]
    )
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        result = check_learn_args(args)
        assert result == 1

    # Test without merge flag but existing checklist
    args = parser.parse_args(
        [
            "learn",
            "--api-key",
            "test-key",
            "--url",
            "https://example.com",
        ]
    )
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        result = check_learn_args(args)
        assert result == 1

    # Test with merge flag and existing checklist
    args = parser.parse_args(
        [
            "learn",
            "--api-key",
            "test-key",
            "--url",
            "https://example.com",
            "--merge",
        ]
    )
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        result = check_learn_args(args)
        assert isinstance(result, argparse.Namespace)
        assert result.api_key == "test-key"
        assert result.command == "learn"
        assert result.url == "https://example.com"
        assert result.merge is True
