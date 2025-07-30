import re
from typing import List, Literal, Any, Union
from functools import cached_property
from pathlib import Path
import zipfile
import requests
import io

# Define a constant for the ANSI escape code pattern
ANSI_ESCAPE_CODE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    """
    Removes ANSI escape codes from a string.

    Args:
        text (str): The string potentially containing ANSI escape codes.

    Returns:
        str: The string with ANSI codes removed.
    """
    return ANSI_ESCAPE_CODE_PATTERN.sub("", text)


def ansi_width(text: str) -> int:
    """
    Calculates the width of a string after removing ANSI escape sequences.

    Args:
        text (str): The string potentially containing ANSI escape codes.

    Returns:
        int: The width of the string without ANSI codes.
    """
    return len(strip_ansi(text))


def align_lines(
    lines: List[str],
    target_width: int,
    align: Literal["start", "center", "end"],
) -> List[str]:
    """
    Aligns a list of strings to a specified target width.

    Args:
        lines (List[str]): List of strings to align.
        target_width (int): The width to align each line to.
        align (Literal["start", "center", "end"]): Alignment type.

    Returns:
        List[str]: List of aligned strings.
    """
    aligned_lines = []
    for line in lines:
        padding = max(target_width - ansi_width(line), 0)
        if align == "start":
            aligned_lines.append(line + " " * padding)
        elif align == "center":
            left_padding = padding // 2
            right_padding = padding - left_padding
            aligned_lines.append(" " * left_padding + line + " " * right_padding)
        elif align == "end":
            aligned_lines.append(" " * padding + line)
        else:
            raise ValueError(f"Invalid alignment type: {align}")
    return aligned_lines


class Layout:
    """
    Arranges elements horizontally or vertically with optional alignment and dividers.

    Layout is used for pretty-printing and organizing visual representations of ARC objects
    in the terminal or as string output.

    Args:
        *elements (Any): Elements to arrange (strings or objects with __repr__).
        direction (Literal["horizontal", "vertical"]): Layout direction.
        align (Literal["start", "center", "end"]): Alignment of elements.
        show_divider (bool): Whether to show dividers between elements.
        min_width (int): Minimum width for the layout.

    Properties:
        width (int): Maximum width of the layout's string representation.
        height (int): Number of lines in the layout's string representation.
    """

    def __init__(
        self,
        *elements: Any,
        direction: Literal["horizontal", "vertical"] = "horizontal",
        align: Literal["start", "center", "end"] = "start",
        show_divider: bool = False,
        min_width: int = 0,
    ):
        """Initializes the Layout."""
        self.elements = elements
        self.direction: Literal["horizontal", "vertical"] = direction
        self.align: Literal["start", "center", "end"] = align
        self.show_divider = show_divider
        self.min_width = min_width

    @cached_property
    def _repr_elements_lines(self) -> List[List[str]]:
        """
        Cached list of string representations of elements, split into lines.

        Returns:
            List[List[str]]: Each element's string representation split into lines.
        """
        return [
            (element if isinstance(element, str) else repr(element)).splitlines()
            for element in self.elements
        ]

    @cached_property
    def width(self) -> int:
        """
        Returns the maximum width of the layout's string representation.

        Returns:
            int: Maximum width.
        """
        return (
            max(
                ansi_width(line)
                for lines in self._repr_elements_lines
                for line in lines
            )
            if self._repr_elements_lines
            else 0
        )

    @cached_property
    def height(self) -> int:
        """
        Returns the number of lines in the layout's string representation.

        Returns:
            int: Number of lines.
        """
        return (
            max(len(lines) for lines in self._repr_elements_lines)
            if self._repr_elements_lines
            else 0
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the layout.

        Returns:
            str: The formatted layout as a string.
        """
        if not self._repr_elements_lines:
            return ""

        if self.direction == "horizontal":
            max_height = max(len(element) for element in self._repr_elements_lines)
            normalized_elements = [
                element + [""] * (max_height - len(element))
                for element in self._repr_elements_lines
            ]
            widths = [
                max(ansi_width(line) for line in element)
                for element in normalized_elements
            ]
            aligned_elements = [
                align_lines(element, width, self.align)
                for element, width in zip(normalized_elements, widths)
            ]
            divider = " | " if self.show_divider else ""
            lines = [
                divider.join(
                    aligned_elements[col][row] for col in range(len(aligned_elements))
                )
                for row in range(max_height)
            ]
            return "\n".join(align_lines(lines, self.min_width, self.align))

        elif self.direction == "vertical":
            max_width = max(
                max(ansi_width(line) for line in element)
                for element in self._repr_elements_lines
            )
            aligned_elements = [
                align_lines(element, max_width, self.align)
                for element in self._repr_elements_lines
            ]
            divider = "\n" + "-" * max_width if self.show_divider else ""
            return f"{divider}\n".join(
                "\n".join(element) for element in aligned_elements
            )
        else:
            raise ValueError(f"Invalid direction: {self.direction}")

    def __str__(self) -> str:
        """
        Returns the same string representation as __repr__.

        Returns:
            str: The formatted layout as a string.
        """
        return self.__repr__()


def download_from_github(
    repo_owner: str,
    repo_name: str,
    path: str,
    branch: str = "main",
    destination: Union[str, Path] = "./downloaded",
) -> None:
    """
    Downloads and extracts a specific path from a GitHub repository.

    Args:
        repo_owner (str): Owner of the GitHub repository.
        repo_name (str): Name of the GitHub repository.
        path (str): Path within the repository to download.
        branch (str): Branch to download from (default: "main").
        destination (str | Path): Local directory to extract files to.

    Raises:
        requests.exceptions.RequestException: If the download fails.
        zipfile.BadZipFile: If the downloaded file is not a valid zip.
        Exception: For other errors during extraction.
    """
    url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/{branch}.zip"
    print(f"Downloading from {url}")
    destination = Path(destination)
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            repo_folder = f"{repo_name}-{branch}/"
            target_folder = f"{repo_folder}{path}/"

            extracted_files = 0
            for file in zip_file.namelist():
                if file.startswith(target_folder) and not file.endswith("/"):
                    relative_path = file[len(target_folder) :]
                    save_path = destination / relative_path
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    with zip_file.open(file) as source, open(save_path, "wb") as target:
                        target.write(source.read())
                    extracted_files += 1

            print(
                f"✅ Successfully downloaded '{path}' from {repo_owner}/{repo_name} into '{destination}'."
                if extracted_files > 0
                else f"⚠️ No files extracted. Check if the path '{path}' exists in the repository."
            )
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download from {url}: {e}")
    except zipfile.BadZipFile:
        print("❌ Failed to extract from the downloaded zip file.")
    except Exception as e:
        print(f"❌ An unexpected error occurred during download or extraction: {e}")


class Link:
    def __init__(self, path: Union[Path, str]) -> None:
        self.path = Path(path)

    def __repr__(self) -> str:
        return str(self.path)

    def _repr_html_(self) -> str:
        return f'<a href="{str(self.path)}">{str(self.path)}</a>'
