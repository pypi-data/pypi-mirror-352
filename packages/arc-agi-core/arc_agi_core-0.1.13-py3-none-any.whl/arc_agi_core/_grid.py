from __future__ import annotations

import json
from pathlib import Path
from typing import List, Union, Self, Tuple
from copy import deepcopy

from ._symbols import Symbol, ANSI_PALETTE, CSS_PALETTE, symbol_values
from ._errors import ArcError
import svg
from ._utils import Link

import numpy as np
from numpy.typing import NDArray
import random


class Grid:
    """
    Represents a 2D grid for ARC tasks, supporting serialization, visualization, and comparison.

    The Grid class is the core data structure for representing ARC input/output grids.
    It provides methods for loading and saving grids in various formats (JSON, NPY, SVG),
    as well as utilities for visualization, comparison, and conversion.

    Methods:
        load_json(path): Load a grid from a JSON file.
        load_npy(path): Load a grid from a NumPy .npy file.
        save_json(path): Save the grid to a JSON file.
        save_npy(path): Save the grid to a NumPy .npy file.
        save_svg(path): Save the grid as an SVG image.
        to_list(): Convert the grid to a nested Python list.
        to_numpy(): Return a copy of the underlying NumPy array.
        to_json(): Serialize the grid as a JSON string.
        __eq__(other): Check equality with another grid.
        __sub__(other): Count differing cells between two grids.
        __hash__(): Compute a hash of the grid's contents.
        __repr__(): Return an ANSI-colored string representation.
        __str__(): Return a plain string representation.
        _repr_html_(): Return an HTML representation for Jupyter/IPython.
        __copy__(): Return a shallow copy of the grid.
        __deepcopy__(memo): Return a deep copy of the grid.

    Properties:
        width (int): Width of the grid (number of columns).
        height (int): Height of the grid (number of rows).
        shape (tuple[int, int]): (height, width) of the grid.
    """

    def __init__(self, array: Union[List[List[int]], NDArray]) -> None:
        """
        Initialize a Grid instance.

        Args:
            array (List[List[int]] | np.ndarray): 2D list or NumPy array of symbol values.

        Raises:
            ArcError: If the array is not 2D or contains invalid symbol values.
        """
        np_array = np.asarray(array, dtype=np.uint8)
        if np_array.ndim != 2:
            raise ArcError("Grid array must be 2D")
        symbols = {s.value for s in Symbol}
        if not set(np_array.flat).issubset(symbols):
            raise ArcError(f"Grid values must be one of the symbols: {sorted(symbols)}")
        self._array = np_array

    @classmethod
    def load_json(cls, path: Union[str, Path]) -> Self:
        """
        Load a Grid from a JSON file.

        Args:
            path (str | Path): Path to the JSON file.

        Returns:
            Grid: The loaded Grid instance.

        Raises:
            ArcError: If loading or parsing fails.
        """
        try:
            data = json.loads(Path(path).read_text())
        except Exception as e:
            raise ArcError(f"Failed to load JSON from {path}: {e}") from e
        return cls(data)

    @classmethod
    def load_npy(cls, path: Union[str, Path]) -> Self:
        """
        Load a Grid from a NumPy .npy file.

        Args:
            path (str | Path): Path to the .npy file.

        Returns:
            Grid: The loaded Grid instance.

        Raises:
            ArcError: If loading fails.
        """
        try:
            arr = np.load(path)
        except Exception as e:
            raise ArcError(f"Failed to load .npy from {path}: {e}") from e
        return cls(arr)

    def save_json(self, path: Union[str, Path]) -> Link:
        """
        Save the grid to a JSON file.

        Args:
            path (str | Path): Destination file path.

        Returns:
            Link: FileLink to the saved file.

        Raises:
            ArcError: If saving fails.
        """
        try:
            path = Path(path)
            if path.suffix != ".json":
                path = path.with_suffix(".json")
            path.write_text(self.to_json())
            return Link(path)
        except Exception as e:
            raise ArcError(f"Failed to save JSON to {path}: {e}") from e

    def save_npy(self, path: Union[str, Path]) -> Link:
        """
        Save the grid to a NumPy .npy file.

        Args:
            path (str | Path): Destination file path.

        Returns:
            Link: FileLink to the saved file.

        Raises:
            ArcError: If saving fails.
        """
        try:
            path = Path(path)
            if path.suffix != ".npy":
                path = path.with_suffix(".npy")
            np.save(path, self._array)
            return Link(path)
        except Exception as e:
            raise ArcError(f"Failed to save .npy to {path}: {e}") from e

    def _draw_svg(
        self,
        origin: Tuple[float, float] = (0, 0),
        cell_size: float = 20,
        stroke_width: float = 1,
    ) -> svg.SVG:
        cells = []
        for y, row in enumerate(self.to_list()):
            for x, cell in enumerate(row):
                cells.append(
                    svg.Rect(
                        x=origin[0] + x * cell_size,
                        y=origin[1] + y * cell_size,
                        stroke_width=stroke_width,
                        stroke="grey",
                        width=cell_size,
                        height=cell_size,
                        fill=CSS_PALETTE[Symbol(cell)],
                        data={"x": str(x), "y": str(y), "symbol": str(cell)},
                    )
                )
        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                min_x=origin[0] - stroke_width / 2,
                min_y=origin[1] - stroke_width / 2,
                width=cell_size * self.width + stroke_width,
                height=cell_size * self.height + stroke_width,
            ),
            elements=cells + [svg.Desc(text=self.to_json()), svg.Title(content="Grid")],
        )

    def save_svg(self, path: Union[str, Path]) -> Link:
        """
        Save the grid as an SVG file.

        Args:
            path (str | Path): Destination file path.

        Returns:
            Link: FileLink to the saved SVG.

        Raises:
            ArcError: If saving fails.
        """
        try:
            path = Path(path)
            if path.suffix != ".svg":
                path = path.with_suffix(".svg")
            svg_string = self._draw_svg().as_str()
            path.write_text(svg_string)
            return Link(path)
        except Exception as e:
            raise ArcError(f"Failed to save .svg to {path}: {e}") from e

    def to_list(self) -> List[List[int]]:
        """
        Convert the grid to a nested Python list.

        Returns:
            List[List[int]]: The grid as a list of lists.
        """
        return self._array.tolist()  # type: ignore  # Did not want to complicate this

    def to_numpy(self) -> NDArray:
        """
        Return a copy of the underlying NumPy array.

        Returns:
            np.ndarray: The grid as a NumPy array.
        """
        return self._array.copy()

    def to_json(self) -> str:
        """
        Serialize the grid as a JSON string.

        Returns:
            str: The grid in JSON format.
        """
        return json.dumps(self.to_list())

    @property
    def width(self) -> int:
        """
        Get the width of the grid (number of columns).

        Returns:
            int: Width of the grid.
        """
        return self._array.shape[1]

    @property
    def height(self) -> int:
        """
        Get the height of the grid (number of rows).

        Returns:
            int: Height of the grid.
        """
        return self._array.shape[0]

    @property
    def shape(self) -> tuple[int, int]:
        """
        Get the shape of the grid as (height, width).

        Returns:
            tuple[int, int]: (height, width) of the grid.
        """
        return (self.height, self.width)

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Grid.

        Args:
            other (object): Another Grid instance.

        Returns:
            bool: True if grids are equal, False otherwise.

        Raises:
            NotImplementedError: If other is not a Grid.
        """
        if not isinstance(other, Grid):
            raise NotImplementedError
        return np.array_equal(self._array, other._array)

    def __sub__(self, other: object) -> int:
        """
        Count the number of differing cells between two grids.

        Args:
            other (object): Another Grid instance.

        Returns:
            int: Number of differing cells.

        Raises:
            NotImplementedError: If other is not a Grid or shapes differ.
        """
        if not isinstance(other, Grid):
            raise NotImplementedError
        if self.shape != other.shape:
            raise NotImplementedError
        return int((self._array != other._array).sum())

    def __hash__(self) -> int:
        """
        Compute a hash of the grid's contents.

        Returns:
            int: Hash value.
        """
        return abs(
            hash((self._array.shape, str(self._array.dtype), self._array.tobytes()))
        )

    def __repr__(self) -> str:
        """
        Return an ANSI-colored string representation of the grid.

        Returns:
            str: ANSI-colored grid. Returns `<Grid (Not initialized)>` if the grid is not initialized.
        """
        if self._array is None:
            return "<Grid (Not initialized)>"
        return "\n".join(
            "".join(ANSI_PALETTE[Symbol(v)] for v in r) for r in self.to_list()
        )

    def __str__(self) -> str:
        """
        Return a plain string representation of the grid.

        Returns:
            str: Plain grid as space-separated values.
        """
        return "\n".join(" ".join(map(str, row)) for row in self.to_list())

    def _repr_html_(self) -> str:
        """
        Return an HTML representation of the grid for Jupyter/IPython.

        Returns:
            str: HTML string.
        """
        return (
            f'<div class="grid" style="display: grid; grid-template-columns: repeat({self.width}, 1rem); grid-template-rows: repeat({self.height}, 1rem); width: fit-content; height: fit-content; margin: auto;">'
            + " ".join(
                f'<div class="cell" data-x="{x}" data-y="{y}" data-symbol="{value}" style="width: 1rem; height: 1rem; background-color: {CSS_PALETTE[Symbol(value)]}; border: solid 1px dimgrey"></div>'
                for y, row in enumerate(self.to_list())
                for x, value in enumerate(row)
            )
            + "</div>"
        )

    def __copy__(self) -> Self:
        """
        Return a shallow copy of the grid.

        Returns:
            Grid: A new Grid instance with the same array reference.
        """
        return type(self)(self._array)

    def __deepcopy__(self, memo) -> Self:
        """
        Return a deep copy of the grid.

        Args:
            memo (dict): Memoization dictionary for deepcopy.

        Returns:
            Grid: A new Grid instance with a deep-copied array.
        """
        return type(self)(deepcopy(self._array, memo))

    @classmethod
    def random(cls) -> Self:
        """
        Generate a random Grid instance.

        The grid will have random dimensions between 1 and 30 (inclusive)
        and its cells will contain random valid symbol values.

        Returns:
            Grid: A randomly generated Grid instance.
        """
        width = random.randint(1, 30)
        height = random.randint(1, 30)
        return cls(np.random.choice(list(symbol_values), size=(height, width)))
