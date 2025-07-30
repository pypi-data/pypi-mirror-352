import os
from ara_cli.artefact_models.artefact_load import artefact_from_content


class TagExtractor:
    def __init__(self, file_system=None):
        self.file_system = file_system or os

    def extract_tags(self, navigate_to_target=False):
        from ara_cli.template_manager import DirectoryNavigator
        from ara_cli.artefact_reader import ArtefactReader

        navigator = DirectoryNavigator()
        if navigate_to_target:
            navigator.navigate_to_target()

        artefacts = ArtefactReader.read_artefacts()

        unique_tags = set()

        for artefact_list in artefacts.values():
            for artefact in artefact_list:
                user_tags = [f"user_{tag}" for tag in artefact.users]
                tags = [tag for tag in (artefact.tags + [artefact.status] + user_tags) if tag is not None]
                unique_tags.update(tags)

        sorted_tags = sorted(unique_tags)
        return sorted_tags
