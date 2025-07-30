import pytest
from unittest.mock import patch, mock_open, Mock
from ara_cli.artefact_reader import ArtefactReader
from ara_cli.artefact import Artefact

@pytest.mark.parametrize("artefact_name, classifier, is_valid, file_paths, expected_output, should_suggest", [
    ("artefact1", "example", True, ["/example/artefact1.example"], ("file content", "/example/artefact1.example"), False),
    ("artefact2", "invalid_classifier", False, ["/invalid_classifier/artefact2.invalid_classifier"], None, False),
    ("artefact3", "example", True, [], None, True),
])
def test_read_artefact(artefact_name, classifier, is_valid, file_paths, expected_output, should_suggest):
    original_directory = "/original/directory"

    with patch('os.getcwd', return_value=original_directory), \
         patch('os.chdir') as mock_chdir, \
         patch('ara_cli.directory_navigator.DirectoryNavigator.navigate_to_target'), \
         patch('ara_cli.classifier.Classifier.is_valid_classifier', return_value=is_valid), \
         patch('ara_cli.file_classifier.FileClassifier.classify_files', return_value={classifier: file_paths}), \
         patch('builtins.open', mock_open(read_data="file content")) as mock_file, \
         patch('ara_cli.artefact_fuzzy_search.suggest_close_name_matches') as mock_suggest:

        if expected_output is None:
            expected_content, expected_file_path = None, None
        else:
            expected_content, expected_file_path = expected_output

        content, file_path = ArtefactReader.read_artefact(artefact_name, classifier)

        # Check if the content and file path match expected output
        assert content == expected_content
        assert file_path == expected_file_path

        # Check the directory was changed back to original
        mock_chdir.assert_called_with(original_directory)

        if not is_valid:
            mock_file.assert_not_called()
            mock_suggest.assert_not_called()  # Suggestion would not be called for invalid classifier
        elif not file_paths:
            mock_file.assert_not_called()
            if not should_suggest:
                mock_suggest.assert_not_called()
        else:
            mock_file.assert_called_once_with(expected_file_path, 'r')
            mock_suggest.assert_not_called()  # Suggestion should not be called if a valid artefact is found

@pytest.mark.parametrize("artefact_content, artefact_titles, expected_output", [
    ("Contributes to: parent_name Example", ["Example"], ("parent_name", "Example")),
    ("Contributes to parent_name Example", ["Example"], ("parent_name", "Example")),
    ("Contributes to : parent_name Feature", ["Example", "Feature"], ("parent_name", "Feature")),
    ("No contribution information here.", ["Example"], (None, None)),
    ("Contributes to : parent_name NotListedTitle", ["Example"], (None, None)),
])
def test_extract_parent_tree(artefact_content, artefact_titles, expected_output):
    with patch('ara_cli.classifier.Classifier.artefact_titles', return_value=artefact_titles):
        parent_name, parent_type = ArtefactReader.extract_parent_tree(artefact_content)
        assert (parent_name, parent_type) == expected_output
