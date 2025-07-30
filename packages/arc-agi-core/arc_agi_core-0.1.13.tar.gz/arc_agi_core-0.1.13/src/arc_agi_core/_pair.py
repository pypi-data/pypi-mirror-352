from typing import Union, List, Optional, Dict, Self, Tuple
from ._grid import Grid
from ._utils import Layout, Link

import warnings
from pathlib import Path
import json
from ._errors import ArcError
from copy import deepcopy
import svg
from math import sqrt


class Pair:
    """
    Represents a single input-output pair for an ARC task.

    A Pair consists of an input grid and an output grid, with optional censoring
    of the output (for use in test sets where the output is hidden).

    Attributes:
        input (Grid): The input grid for the pair.
        output (Optional[Grid]): The output grid for the pair, or None if censored.
        _is_censored (bool): Whether the output is currently censored.

    Methods:
        censor(): Censor the output grid (hide it).
        uncensor(): Uncensor the output grid (reveal it).
        to_dict(): Convert the pair to a dictionary format.
        to_json(): Serialize the pair as a JSON string.
        save_json(path): Save the pair to a JSON file.
        load_json(path): Load a pair from a JSON file.
        save_svg(path): Save the pair as an SVG image.
        __hash__(): Compute a hash of the pair (prohibited if censored).
        __eq__(other): Check equality with another pair (prohibited if censored).
        __repr__(): Return a string representation.
        _repr_html_(): Return an HTML representation for Jupyter/IPython.
        __copy__(): Create a shallow copy of the pair.
        __deepcopy__(): Create a deep copy of the pair.
    """

    def __init__(
        self,
        input: Union[Grid, List[List[int]]],
        output: Union[Grid, List[List[int]], None],
        censor: bool = False,
    ) -> None:
        """
        Initialize a Pair instance.

        Args:
            input (Grid | List[List[int]]): The input grid or nested list.
            output (Grid | List[List[int]] | None): The output grid or nested list.
            censor (bool): Whether to censor the output initially.
        """
        self.input = input if isinstance(input, Grid) else Grid(input)
        self.output = output
        self._is_censored = True if censor is None else censor

    @property
    def output(self) -> Optional[Grid]:
        """
        Get the output grid, or None if censored.

        Returns:
            Optional[Grid]: The output grid, or None if censored.

        Warns:
            UserWarning: If the output is censored, a warning is issued and None is returned.
        """
        if self._is_censored:
            warnings.warn(
                "Accessing a censored output. `None` is returned. Call `.uncensor()` to gain access.",
                UserWarning,
                stacklevel=2,
            )
            return None
        return self._output

    @output.setter
    def output(self, grid: Union[Grid, List[List[int]], None]) -> None:
        """
        Set the output grid.

        Args:
            grid (Grid | List[List[int]]): The output grid or nested list.
        """
        self._output = grid if (isinstance(grid, Grid) or grid is None) else Grid(grid)

    def censor(self) -> Self:
        """
        Censor the output grid (hide it).

        Returns:
            Self: The Pair instance (for chaining).
        """
        self._is_censored = True
        return self

    def uncensor(self) -> Self:
        """
        Uncensor the output grid (reveal it).

        Returns:
            Self: The Pair instance (for chaining).
        """
        self._is_censored = False
        return self

    def _repr_html_(self) -> str:
        """
        Return an HTML representation of the pair for Jupyter/IPython.

        Returns:
            str: HTML string showing input and output (or *CENSORED* if censored).
        """
        if self._output:
            if self._is_censored:
                output_repr = "<div>*CENSORED*</div>"
            else:
                output_repr = self._output._repr_html_()
        else:
            output_repr = "<div>* N/A *</div>"
        return (
            '<div class="pair" style="display: flex; align-items: center; gap: 1rem; width: fit-content; height: fit-content; margin: auto;">'
            f"<div>{self.input._repr_html_()}</div>"
            "<div> → </div>"
            f"<div>{output_repr}</div>"
            "</div>"
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the pair, showing input and output.

        Returns:
            str: String representation, with *CENSORED* if output is censored.
        """
        if self._output:
            if self._is_censored:
                output_repr = "*CENSORED*"
            else:
                output_repr = repr(self._output)
        else:
            output_repr = "* N/A *"
        return repr(
            Layout(
                Layout(
                    "INPUT",
                    repr(self.input),
                    direction="vertical",
                    align="center",
                ),
                "->",
                Layout(
                    "OUTPUT",
                    output_repr,
                    direction="vertical",
                    align="center",
                ),
                align="center",
            )
        )

    def __hash__(self) -> int:
        """
        Compute a hash of the pair based on input and output.

        Returns:
            int: Hash value.

        Warns:
            UserWarning: If the output is censored, a warning is issued and 0 is returned.
        """
        if self._is_censored:
            warnings.warn(
                "Hash of a censored pair is prohibited to prevent leakage through equality check. Call `.uncensor()` to gain access.",
                UserWarning,
                stacklevel=2,
            )
            return 0
        return abs(hash((self.input, self._output)))

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Pair.

        Args:
            other (object): Another Pair instance.

        Returns:
            bool: True if input and output grids are equal and not censored.

        Warns:
            UserWarning: If the output is censored, a warning is issued and False is returned.

        Raises:
            NotImplementedError: If other is not a Pair.
        """
        if not isinstance(other, Pair):
            raise NotImplementedError
        if self._is_censored:
            warnings.warn(
                "Equality check of a censored pair is prohibited to prevent leakage. Call `.uncensor()` to gain access.",
                UserWarning,
                stacklevel=2,
            )
            return False
        return (self.input == other.input) and (self._output == other.output)

    def to_dict(self) -> Dict[str, Optional[List[List[int]]]]:
        """
        Convert the pair to a dictionary format.

        Returns:
            Dict[str, Optional[List[List[int]]]]: Dictionary with 'input' and 'output' keys.
                If censored, 'output' is None.

        Warns:
            UserWarning: If the output is censored, a warning is issued.
        """
        if self._is_censored:
            warnings.warn(
                "Censored output is not included. Call `.uncensor()` to reveal it.",
                UserWarning,
                stacklevel=2,
            )
        if self._output:
            return {
                "input": self.input.to_list(),
                "output": self._output.to_list(),
            }
        else:
            return {
                "input": self.input.to_list(),
            }

    def to_json(self) -> str:
        """
        Serialize the pair as a JSON string.

        Returns:
            str: The pair in JSON format.
        """
        return json.dumps(self.to_dict())

    def save_json(self, path: Union[str, Path]) -> Link:
        """
        Save the pair to a JSON file.

        Args:
            path (str | Path): Destination file path.

        Returns:
            Link: IPython FileLink to the saved file.

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

    @classmethod
    def load_json(cls, path: Union[str, Path]) -> Self:
        """
        Load a pair from a JSON file.

        Args:
            path (str | Path): Path to the JSON file.

        Returns:
            Pair: The loaded Pair instance.

        Raises:
            ArcError: If loading fails.
        """
        try:
            path = Path(path)
            data = json.loads(path.read_text())
            return cls(data["input"], getattr(data, "output", None))
        except Exception as e:
            raise ArcError(f"Failed to load JSON from {path}: {e}") from e

    def _draw_svg(
        self,
        origin: Tuple[float, float] = (0, 0),
        cell_size: float = 20,
        stroke_width: float = 1,
        left_gap: float = 20,
        right_gap: float = 20,
    ) -> svg.SVG:
        input_svg_width = self.input.width * cell_size
        input_svg_height = self.input.height * cell_size
        output_svg_height = (
            self.input.height
            if (self._is_censored or self._output is None)
            else self._output.height
        ) * cell_size
        output_svg_width = (
            max(output_svg_height * 0.3 / 2, cell_size)
            if (self._is_censored or self._output is None)
            else self._output.width * cell_size
        )
        pair_width = (
            input_svg_width + left_gap + cell_size + right_gap + output_svg_width
        )
        pair_height = max(input_svg_height, output_svg_height)

        input_svg = self.input._draw_svg(
            (origin[0], origin[1] + max((output_svg_height - input_svg_height) / 2, 0)),
            cell_size,
            stroke_width,
        )
        input_svg.overflow = "visible"
        input_svg.viewBox = None
        arrow_svg = [
            svg.Line(
                x1=origin[0] + input_svg_width + left_gap,
                y1=origin[1] + pair_height / 2,
                x2=origin[0] + input_svg_width + left_gap + cell_size,
                y2=origin[1] + pair_height / 2,
                stroke="grey",
                stroke_width=3 * stroke_width,
            ),  # -
            svg.Line(
                x1=origin[0]
                + input_svg_width
                + left_gap
                + cell_size
                + sqrt(stroke_width),
                y1=origin[1] + pair_height / 2 + sqrt(stroke_width),
                x2=origin[0] + input_svg_width + left_gap + cell_size * 0.7,
                y2=origin[1] + pair_height / 2 - cell_size * 0.3,
                stroke="grey",
                stroke_width=3 * stroke_width,
            ),  # \
            svg.Line(
                x1=origin[0]
                + input_svg_width
                + left_gap
                + cell_size
                + sqrt(stroke_width),
                y1=origin[1] + pair_height / 2 - sqrt(stroke_width),
                x2=origin[0] + input_svg_width + left_gap + cell_size * 0.7,
                y2=origin[1] + pair_height / 2 + cell_size * 0.3,
                stroke="grey",
                stroke_width=3 * stroke_width,
            ),  # /
        ]
        if self._is_censored or self._output is None:
            output_svg = svg.Text(
                text="?",
                x=origin[0] + input_svg_width + left_gap + cell_size + right_gap,
                y=origin[1] + pair_height / 2,
                dominant_baseline="central",
                font_size=max(output_svg_height * 0.3, cell_size),
                stroke="grey",
                fill="grey",
            )
        else:
            output_svg = self._output._draw_svg(
                (
                    origin[0] + input_svg_width + left_gap + cell_size + right_gap,
                    origin[1] + max((input_svg_height - output_svg_height) / 2, 0),
                ),
                cell_size,
                stroke_width,
            )
            output_svg.overflow = "visible"
            output_svg.viewBox = None
        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                min_x=origin[0] - stroke_width / 2,
                min_y=origin[1] - stroke_width / 2,
                width=pair_width + stroke_width,
                height=pair_height + stroke_width,
            ),
            elements=[
                input_svg,
                *arrow_svg,
                output_svg,
                svg.Desc(text=self.to_json()),
                svg.Title(content="Pair"),
            ],
        )

    def save_svg(self, path: Union[Path, str]) -> Link:
        """
        Save the pair as an SVG image.

        Args:
            path (str | Path): Destination file path.

        Returns:
            Link: IPython FileLink to the saved SVG file.

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

    def __copy__(self) -> Self:
        """
        Create a shallow copy of the pair.

        Returns:
            Pair: Shallow copy of the pair.
        """
        return type(self)(self.input, self._output, self._is_censored)

    def __deepcopy__(self, memo) -> Self:
        """
        Create a deep copy of the pair.

        Args:
            memo (dict): Memoization dictionary for deepcopy.

        Returns:
            Pair: Deep copy of the pair.
        """
        return type(self)(
            deepcopy(self.input, memo), deepcopy(self._output, memo), self._is_censored
        )

    @classmethod
    def random(cls) -> Self:
        """
        Generate a random Pair instance.

        Both the input and output grids will be randomly generated.

        Returns:
            Pair: A randomly generated Pair instance.
        """
        return cls(Grid.random(), Grid.random())
