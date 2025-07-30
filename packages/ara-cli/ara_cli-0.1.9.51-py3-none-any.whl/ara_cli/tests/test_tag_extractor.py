import pytest
from unittest.mock import MagicMock, patch
from ara_cli.tag_extractor import TagExtractor  # Adjust the import based on your project structure

@pytest.fixture
def artefact():
    """Fixture to create a mock artefact object."""
    class Artefact:
        def __init__(self, tags, status, users):
            self.tags = tags
            self.status = status
            self.users = users

    return Artefact

@pytest.mark.parametrize("navigate_to_target, artefact_data, expected_tags", [
    (False, {'artefacts': [(
        ['tag1', 'tag2'], 'status1', ['user1', 'user2']
    )]}, ['status1', 'tag1', 'tag2', 'user_user1', 'user_user2']),
    (True, {'artefacts': [(
        ['tag3'], 'status2', ['user3']
    )]}, ['status2', 'tag3', 'user_user3'])
])
@patch('ara_cli.template_manager.DirectoryNavigator')
@patch('ara_cli.artefact_reader.ArtefactReader')
def test_extract_tags(mock_artefact_reader, mock_directory_navigator, artefact, navigate_to_target, artefact_data, expected_tags):
    # Mock the artefact reader to return artefact data
    mock_artefact_reader.read_artefacts.return_value = {'key': [artefact(*data) for data in artefact_data['artefacts']]}

    # Mock the directory navigator
    mock_navigator_instance = mock_directory_navigator.return_value
    mock_navigator_instance.navigate_to_target = MagicMock()

    tag_extractor = TagExtractor()

    # Run the extract_tags method
    result = tag_extractor.extract_tags(navigate_to_target=navigate_to_target)

    # Assertions
    if navigate_to_target:
        mock_navigator_instance.navigate_to_target.assert_called_once()
    else:
        mock_navigator_instance.navigate_to_target.assert_not_called()

    assert result == expected_tags