import pytest
from unittest.mock import patch, MagicMock, mock_open, call
from ara_cli.artefact_scan import check_file, find_invalid_files, show_results
from pydantic import ValidationError


def test_check_file_valid():
    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.return_value = None

    with patch("builtins.open", mock_open(read_data="valid content")):
        is_valid, reason = check_file("dummy_path", mock_artefact_class)
        assert is_valid is True
        assert reason is None


def test_check_file_value_error():
    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.side_effect = ValueError("Value error")

    with patch("builtins.open", mock_open(read_data="invalid content")):
        is_valid, reason = check_file("dummy_path", mock_artefact_class)
        assert is_valid is False
        assert "Value error" in reason


def test_check_file_assertion_error():
    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.side_effect = AssertionError(
        "Assertion error")

    with patch("builtins.open", mock_open(read_data="invalid content")):
        is_valid, reason = check_file("dummy_path", mock_artefact_class)
        assert is_valid is False
        assert "Assertion error" in reason


def test_check_file_os_error():
    mock_artefact_class = MagicMock()

    with patch("builtins.open", side_effect=OSError("File not found")):
        is_valid, reason = check_file("dummy_path", mock_artefact_class)
        assert is_valid is False
        assert "File error: File not found" in reason


def test_check_file_unexpected_error():
    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.side_effect = Exception("Unexpected error")

    with patch("builtins.open", mock_open(read_data="content")):
        is_valid, reason = check_file("dummy_path", mock_artefact_class)
        assert is_valid is False
        assert "Unexpected error: Exception('Unexpected error')" in reason

# Tests for find_invalid_files


def test_find_invalid_files():
    mock_artefact_class = MagicMock()
    with patch("ara_cli.artefact_models.artefact_mapping.artefact_type_mapping", {"test_classifier": mock_artefact_class}):
        artefact_files = {
            "test_classifier": [{"file_path": "file1.txt"}, {"file_path": "file2.txt"}, {"file_path": "templates/file3.txt"}]
        }

        with patch("ara_cli.artefact_scan.check_file") as mock_check_file:
            mock_check_file.side_effect = [
                (True, None),           # file1.txt
                (False, "Invalid content")  # file2.txt
            ]

            invalid_files = find_invalid_files(
                artefact_files, "test_classifier")
            assert len(invalid_files) == 1
            assert invalid_files[0] == ("file2.txt", "Invalid content")
            mock_check_file.assert_has_calls([
                call("file1.txt", mock_artefact_class),
                call("file2.txt", mock_artefact_class)
            ], any_order=False)

# Tests for show_results


def test_show_results_no_issues(capsys):
    invalid_artefacts = {}
    with patch("builtins.open", mock_open()) as m:
        show_results(invalid_artefacts)
        captured = capsys.readouterr()
        assert captured.out == "All files are good!\n"
        m.assert_called_once_with("incompatible_artefacts_report.md", "w")
        handle = m()
        handle.write.assert_has_calls([
            call("# Artefact Check Report\n\n"),
            call("No problems found.\n")
        ], any_order=False)


def test_show_results_with_issues(capsys):
    invalid_artefacts = {
        "classifier1": [("file1.txt", "reason1"), ("file2.txt", "reason2")],
        "classifier2": [("file3.txt", "reason3")]
    }
    with patch("builtins.open", mock_open()) as m:
        show_results(invalid_artefacts)
        captured = capsys.readouterr()
        expected_output = (
            "\nIncompatible classifier1 Files:\n"
            "\t- file1.txt\n"
            "\t- file2.txt\n"
            "\nIncompatible classifier2 Files:\n"
            "\t- file3.txt\n"
        )
        assert captured.out == expected_output
        m.assert_called_once_with("incompatible_artefacts_report.md", "w")
        handle = m()
        expected_writes = [
            call("# Artefact Check Report\n\n"),
            call("## classifier1\n"),
            call("- `file1.txt`: reason1\n"),
            call("- `file2.txt`: reason2\n"),
            call("\n"),
            call("## classifier2\n"),
            call("- `file3.txt`: reason3\n"),
            call("\n")
        ]
        handle.write.assert_has_calls(expected_writes, any_order=False)
