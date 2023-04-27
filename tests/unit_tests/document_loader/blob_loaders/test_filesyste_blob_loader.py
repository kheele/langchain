"""Verify that file system blob loader works as expected."""
import os
import tempfile
from pathlib import Path
from typing import Generator, Sequence

import pytest

from langchain.document_loaders.blob_loaders import FileSystemBlobLoader


@pytest.fixture
def toy_dir() -> Generator[Path, None, None]:
    """Yield a pre-populated directory to test the blob loader."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test.txt
        with open(os.path.join(temp_dir, "test.txt"), "w") as test_txt:
            test_txt.write("This is a test.txt file.")

        # Create test.html
        with open(os.path.join(temp_dir, "test.html"), "w") as test_html:
            test_html.write(
                "<html><body><h1>This is a test.html file.</h1></body></html>"
            )

        # Create .hidden_file
        with open(os.path.join(temp_dir, ".hidden_file"), "w") as hidden_file:
            hidden_file.write("This is a hidden file.")

        # Create some_dir/nested_file.txt
        some_dir = os.path.join(temp_dir, "some_dir")
        os.makedirs(some_dir)
        with open(os.path.join(some_dir, "nested_file.txt"), "w") as nested_file:
            nested_file.write("This is a nested_file.txt file.")

        yield Path(temp_dir)


@pytest.mark.parametrize(
    "glob, relative_filenames",
    [
        (
            "**/[!.]*",
            ["test.html", "test.txt", "some_dir/nested_file.txt"],
        ),
        ("*", ["test.html", "test.txt", ".hidden_file"]),
        ("**/*.html", ["test.html"]),
        ("*/*.txt", ["some_dir/nested_file.txt"]),
        ("meeeeeeow", []),
    ],
)
def test_file_names_exist(
    toy_dir: Path,
    glob: str,
    relative_filenames: Sequence[str],
) -> None:
    """Verify that the file names exist."""
    loader = FileSystemBlobLoader(
        path=toy_dir,
        glob=glob,
    )
    blobs = list(loader.yield_blobs())

    file_names = sorted(blob.path for blob in blobs)

    expected_filenames = sorted(
        str(toy_dir / relative_filename) for relative_filename in relative_filenames
    )

    assert file_names == expected_filenames