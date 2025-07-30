#!/usr/bin/env python3
"""
analyse_artefacts.py

Walk a directory tree, try to deserialize every *.vision *.epic *.task … file
with the appropriate Pydantic artefact model, and write the list of files that
fail validation (plus the reason) to 'invalid_artefacts.txt'.
"""

"""
python analyse_artefacts.py <path_to_ara_folder ex: ./ara/>
"""

from ara_cli.artefact_models import businessgoal_artefact_model, capability_artefact_model, epic_artefact_model, example_artefact_model, feature_artefact_model, issue_artefact_model, keyfeature_artefact_model, userstory_artefact_model, task_artefact_model, vision_artefact_model
from ara_cli.artefact_models.artefact_model import Artefact, ArtefactType
from pydantic import ValidationError
from typing import Dict, Type, List, Tuple
from pathlib import Path
import os
import sys


# --- import your domain model ----------------------------------------------
# Make sure this import path matches your project layout.
# (e.g. from ara_cli.artefact_model import Artefact, ArtefactType)
# ---------------------------------------------------------------------------


def build_type_map() -> Dict[ArtefactType, Type[Artefact]]:
    type_map: Dict[ArtefactType, Type[Artefact]] = {}
    queue: List[Type[Artefact]] = list(Artefact.__subclasses__())
    while queue:
        cls = queue.pop()
        try:
            artefact_type = cls._artefact_type()
            type_map[artefact_type] = cls
        except Exception:
            pass        # abstract / helper subclass
        queue.extend(cls.__subclasses__())
    if not type_map:
        raise RuntimeError("No concrete Artefact subclasses found!")
    return type_map


def find_artefact_files(root: Path, valid_exts: List[str]) -> List[Path]:
    return [
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lstrip(".") in valid_exts
    ]


def scan_folder(
    root_folder: Path,
    detailed_report: Path,
    names_only_report: Path,
    checklist_report: Path
) -> Tuple[int, int]:
    type_map = build_type_map()
    valid_exts = [t.value for t in type_map]

    artefact_files = find_artefact_files(root_folder, valid_exts)
    bad: List[Tuple[Path, str]] = []

    for file_path in artefact_files:
        artefact_type = ArtefactType(file_path.suffix.lstrip("."))
        artefact_cls = type_map[artefact_type]
        text = file_path.read_text(encoding="utf-8")

        try:
            artefact_cls.deserialize(text)
        except (ValidationError, ValueError, AssertionError) as e:
            bad.append((file_path, str(e)))
        except Exception as e:
            bad.append((file_path, f"Unexpected error: {e!r}"))

    # ───────────── write reports ────────────────────────────────────────────
    if bad:
        # 1) detailed txt
        with detailed_report.open("w", encoding="utf-8") as f:
            f.write("Invalid artefacts (file  →  reason)\n\n")
            for path, err in bad:
                f.write(f"{path}  -->  {err}\n")

        # 2) names-only txt
        with names_only_report.open("w", encoding="utf-8") as f:
            for path, _ in bad:
                f.write(f"{path}\n")

        # 3) markdown checklist
        with checklist_report.open("w", encoding="utf-8") as f:
            f.write("# 📋 Artefact-fix checklist\n\n")
            f.write("Tick a box once you’ve fixed & validated the file.\n\n")
            for path, err in bad:
                f.write(f"- [ ] `{path}` – {err}\n")

        print(
            f"\nFinished. {len(bad)}/{len(artefact_files)} files are invalid."
            f"\nReports generated:"
            f"\n • {detailed_report}"
            f"\n • {names_only_report}"
            f"\n • {checklist_report}"
        )
    else:
        print(f"\nFinished. All {len(artefact_files)} artefacts are valid ✔️")
        # clean up stale files from previous runs
        for p in (detailed_report, names_only_report, checklist_report):
            if p.exists():
                p.unlink()

    return len(artefact_files), len(bad)


# ─────────────────────────────── main ──────────────────────────────────────
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:  python scan_artefacts.py  <folder_to_scan>")
        sys.exit(1)

    root_folder = Path(sys.argv[1]).expanduser().resolve()
    if not root_folder.is_dir():
        print(f"Error: '{root_folder}' is not a directory.")
        sys.exit(1)

    scan_folder(
        root_folder=root_folder,
        detailed_report=Path("invalid_artefacts.txt"),
        names_only_report=Path("invalid_artefact_names.txt"),
        checklist_report=Path("invalid_artefacts_checklist.md"),
    )


if __name__ == "__main__":
    main()
