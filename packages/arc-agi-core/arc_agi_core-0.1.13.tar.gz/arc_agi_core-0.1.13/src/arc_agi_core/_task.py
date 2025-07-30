from typing import List, Optional, Dict, Self, Union, Tuple
from ._pair import Pair
from ._grid import Grid

from pathlib import Path
import json
from ._utils import Layout, Link
from ._errors import ArcError
import warnings
from copy import deepcopy
import svg
import random


class Task:
    """
    Represents an ARC (Abstract Reasoning Corpus) task, consisting of training and test input-output pairs.

    Provides methods for loading from and saving to JSON, converting to and from dictionary representations,
    censoring/uncensoring test outputs, and rendering as string or HTML.

    Attributes:
        train (List[Pair]): List of training input-output pairs.
        test (List[Pair]): List of test input-output pairs.
        task_id (Optional[str]): Unique identifier for the task, if available.

    Methods:
        load_json(file_path): Load a Task from a JSON file.
        to_dict(): Convert the Task to a dictionary.
        to_json(): Serialize the Task as a JSON string.
        save_json(path): Save the Task to a JSON file.
        inputs: List of all input grids (train and test).
        outputs: List of all output grids (train and test), censored outputs will be None.
        censor(): Censor the outputs of the test pairs.
        uncensor(): Uncensor the outputs of the test pairs.
        save_svg(path): Save the task as an SVG image.
        __repr__(): String representation of the Task.
        __str__(): String representation (same as __repr__).
        _repr_html_(): HTML representation for Jupyter/IPython.
        __eq__(other): Check equality with another Task.
        __hash__(): Compute a hash of the Task.
        __copy__(): Create a shallow copy of the Task.
        __deepcopy__(memo): Create a deep copy of the Task.
    """

    def __init__(
        self,
        train: List[Pair],
        test: List[Pair],
        task_id: Optional[str] = None,
    ) -> None:
        """
        Initialize a Task.

        Args:
            train (List[Pair]): List of training input-output pairs.
            test (List[Pair]): List of test input-output pairs.
            task_id (Optional[str]): Unique identifier for the task, if available. If not specified, first 8 letters of __hash__ will be used as the task_id.

        Raises:
            TypeError: If any element in train or test is not a Pair.
        """
        if not all(isinstance(pair, Pair) for pair in train):
            raise TypeError("All elements in 'train' must be Pair objects.")
        if not all(isinstance(pair, Pair) for pair in test):
            raise TypeError("All elements in 'test' must be Pair objects.")

        self.train = train
        self.test = test
        self.task_id = task_id if task_id else str(hash(self))[:8]

    @classmethod
    def load_json(cls, file_path: Union[str, Path]) -> Self:
        """
        Load a Task instance from a JSON file.

        Args:
            file_path (str | Path): Path to the JSON file.

        Returns:
            Task: The loaded Task instance.

        Raises:
            ValueError: If loading or parsing fails.
        """
        file_path = Path(file_path)
        task_id = file_path.stem
        try:
            with file_path.open("r") as f:
                task_data = json.load(f)
            train_pairs = [
                Pair(pair["input"], pair.get("output", None))
                for pair in task_data["train"]
            ]
            test_pairs = [
                Pair(pair["input"], pair.get("output", None))
                for pair in task_data["test"]
            ]
            return cls(train_pairs, test_pairs, task_id)
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Error loading Task from JSON '{file_path}': {e}") from e

    def to_dict(self) -> Dict[str, List[Dict[str, Optional[List[List[int]]]]]]:
        """
        Convert the Task to a dictionary format.

        Returns:
            dict: Dictionary with 'train' and 'test' keys, each mapping to a list of
                dictionaries with 'input' and 'output' keys.
        """
        return {
            "train": [pair.to_dict() for pair in self.train],
            "test": [pair.to_dict() for pair in self.test],
        }

    def to_json(self) -> str:
        """
        Serialize the Task as a JSON string.

        Returns:
            str: The Task in JSON format.
        """
        return json.dumps(self.to_dict())

    def save_json(self, path: Union[str, Path]) -> Link:
        """
        Save the Task to a JSON file.

        Args:
            path (str | Path): Destination file path.

        Returns:
            Link: IPython FileLink to the saved file.

        Raises:
            IOError: If saving fails.
        """
        path = Path(path)
        try:
            if path.suffix != ".json":
                path = path.with_suffix(".json")
            path.write_text(self.to_json())
            return Link(path)
        except IOError as e:
            raise IOError(f"Error saving Task to JSON '{path}': {e}") from e

    @property
    def inputs(self) -> List[Grid]:
        """
        Get a list of all input grids (train and test).

        Returns:
            List[Grid]: All input grids in the task.
        """
        return [pair.input for pair in self.train + self.test]

    @property
    def outputs(self) -> List[Optional[Grid]]:
        """
        Get a list of all output grids (train and test). Censored outputs will be None.

        Returns:
            List[Optional[Grid]]: All output grids in the task.
        """
        return [pair.output for pair in self.train + self.test]

    @property
    def challenge(self) -> Self:
        """
        Creates a 'challenge' version of the task where the output of all test pairs is censored.

        This is useful for simulating the state of a task during evaluation, where the
        model is only given the input grids for the test pairs and must generate the outputs.

        Returns:
            Self: A new Task instance with the same training pairs and censored test pairs.
                  The original task is not modified.

        """
        return type(self)(self.train, [Pair(pair.input, None) for pair in self.test])

    @property
    def solution(self) -> List[Grid]:
        """
        Provides a list of the *uncensored* output grids from the test pairs.

        Note that this property will only return non-None grids. If a test pair's
        output is still censored, it will be excluded from this list.

        Returns:
        """
        return [pair.output for pair in self.test if pair.output]

    def __repr__(self) -> str:
        """
        Return a detailed string representation of the task, including all train and test pairs.

        Returns:
            str: String representation of the Task.
        """
        train_repr = Layout(
            *[
                Layout(
                    Layout(
                        f"INPUT {i}", pair.input, direction="vertical", align="center"
                    ),
                    " -> ",
                    Layout(
                        f"OUTPUT {i}",
                        "*CENSORED*" if pair._is_censored else pair.output,
                        direction="vertical",
                        align="center",
                    ),
                )
                for i, pair in enumerate(self.train)
            ],
            direction="vertical",
        )
        test_repr = Layout(
            *[
                Layout(
                    Layout(
                        f"INPUT {i}", pair.input, direction="vertical", align="center"
                    ),
                    " -> ",
                    Layout(
                        f"OUTPUT {i}",
                        pair.output if not pair._is_censored else "*CENSORED*",
                        direction="vertical",
                        align="center",
                    ),
                )
                for i, pair in enumerate(self.test)
            ],
            direction="vertical",
        )
        width = max(train_repr.width, test_repr.width)
        title = f"< Task - {self.task_id} >".center(width, "=")
        train_title = " Train ".center(width, "-")
        test_title = " Test ".center(width, "-")

        return repr(
            Layout(
                title,
                train_title,
                train_repr,
                test_title,
                test_repr,
                direction="vertical",
            )
        )

    def __str__(self) -> str:
        """
        Return the same string representation as __repr__.

        Returns:
            str: String representation of the Task.
        """
        return self.__repr__()

    def _repr_html_(self):
        """
        Return an HTML representation of the task for Jupyter/IPython.

        Returns:
            str: HTML string.
        """
        return (
            '<div style="display: flex; flex-direction: column; align-items: center; width: fit-content; border: solid 2px grey; border-radius: 0.5rem; padding: 0.5rem; margin: auto;">'
            f'<label style="border-bottom: solid 1px grey; width: 100%; text-align: center; ">Task - {self.task_id}</label>'
            "<table>"
            + " ".join(
                f'<tr style="background: transparent"><td style="text-align: center">test[{i}].input</td><td></td><td style="text-align: center">test[{i}].output</td></tr>'
                f'<tr style="background: transparent"><td>{pair.input._repr_html_()}</td>'
                "<td> → </td>"
                + f'<td style="text-align: center; vertical-align: middle;">{"?" if (pair._is_censored or pair._output is None) else pair._output._repr_html_()}</td>'
                + "</tr>"
                for i, pair in enumerate(self.train)
            )
            + '<tr style="border-bottom: dashed 1px grey; height: 1rem;"></tr>'
            + " ".join(
                f'<tr style="background: transparent"><td style="text-align: center">test[{i}].input</td><td></td><td style="text-align: center">test[{i}].output</td></tr>'
                f'<tr style="background: transparent"><td>{pair.input._repr_html_()}</td>'
                "<td> → </td>"
                + f'<td style="text-align: center; vertical-align: middle;">{"?" if (pair._is_censored or pair._output is None) else pair._output._repr_html_()}</td>'
                + "</tr>"
                for i, pair in enumerate(self.test)
            )
            + "</table>"
            + "</div>"
        )

    def censor(self) -> Self:
        """
        Censor the outputs of the test pairs.

        Returns:
            Self: The Task instance (for chaining).
        """
        for pair in self.test:
            pair.censor()
        return self

    def uncensor(self) -> Self:
        """
        Uncensor the outputs of the test pairs.

        Returns:
            Self: The Task instance (for chaining).
        """
        for pair in self.test:
            pair.uncensor()
        return self

    def _draw_svg(
        self,
        origin: Tuple[float, float] = (0, 0),
        cell_size: float = 20,
        stroke_width: float = 1,
        gap: float = 20,
    ) -> svg.SVG:
        inputs_svg_width = (
            max(input_grid.width for input_grid in self.inputs) * cell_size
        )
        outputs_svg_width = (
            max(
                max(pair.input.height * 0.3 / 2, 1)
                if (pair._is_censored or pair._output is None)
                else pair._output.width
                for pair in self.train + self.test
            )
            * cell_size
        )
        task_svg_width = inputs_svg_width + gap * 2 + cell_size + outputs_svg_width
        elements = []
        y = origin[1]
        elements.append(
            svg.Text(
                text=f"Task - {self.task_id}",
                x=origin[0] + task_svg_width / 2,
                y=origin[1] + cell_size * 3 / 2,
                text_anchor="middle",
                dominant_baseline="central",
                font_size=cell_size,
                stroke="grey",
                fill="grey",
            )
        )
        y += 3 * cell_size
        for pair in self.train:
            pair_svg = pair._draw_svg(
                origin=(
                    origin[0] + (inputs_svg_width - pair.input.width * cell_size) / 2,
                    y,
                ),
                cell_size=cell_size,
                stroke_width=stroke_width,
                left_gap=(inputs_svg_width - pair.input.width * cell_size) / 2 + gap,
                right_gap=(
                    outputs_svg_width
                    - (
                        max(pair.input.height * cell_size * 0.3 / 2, cell_size)
                        if (pair._is_censored or pair._output is None)
                        else pair._output.width * cell_size
                    )
                )
                / 2
                + gap,
            )
            pair_svg.overflow = "visible"
            pair_svg.viewBox = None
            elements.append(pair_svg)
            y += (
                max(
                    pair.input.height,
                    pair.input.height
                    if (pair._is_censored or pair._output is None)
                    else pair._output.height,
                )
                + 1
            ) * cell_size
        elements.append(
            svg.Line(
                x1=origin[0],
                y1=y,
                x2=origin[0] + task_svg_width,
                y2=y,
                stroke_dasharray=[5, 5],
                stroke="grey",
                stroke_width=stroke_width * 3,
            )
        )
        y += cell_size
        for pair in self.test:
            pair_svg = pair._draw_svg(
                origin=(
                    origin[0] + (inputs_svg_width - pair.input.width * cell_size) / 2,
                    y,
                ),
                cell_size=cell_size,
                stroke_width=stroke_width,
                left_gap=(inputs_svg_width - pair.input.width * cell_size) / 2 + gap,
                right_gap=(
                    outputs_svg_width
                    - (
                        max(pair.input.height * cell_size * 0.3 / 2, cell_size)
                        if (pair._is_censored or pair._output is None)
                        else pair._output.width * cell_size
                    )
                )
                / 2
                + gap,
            )
            pair_svg.overflow = "visible"
            pair_svg.viewBox = None
            elements.append(pair_svg)
            y += (
                max(
                    pair.input.height,
                    pair.input.height
                    if (pair._is_censored or pair._output is None)
                    else pair._output.height,
                )
                + 1
            ) * cell_size
        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                min_x=origin[0] - stroke_width / 2,
                min_y=origin[1] - stroke_width / 2,
                width=task_svg_width + stroke_width,
                height=(
                    sum(
                        max(
                            pair.input.height,
                            pair.input.height
                            if (pair._is_censored or pair._output is None)
                            else pair._output.height,
                        )
                        + 1
                        for pair in self.train + self.test
                    )
                    + 3
                )
                * cell_size,
            ),
            elements=elements
            + [
                svg.Desc(text=self.to_json()),
                svg.Title(
                    content=f"Task{' - ' + self.task_id if self.task_id else ''}"
                ),
            ],
        )

    def save_svg(self, path: Union[Path, str]) -> Link:
        """
        Save the task as an SVG image.

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

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Task.

        Args:
            other (object): Another Task instance.

        Returns:
            bool: True if all the pairs in train and test are the same.

        Raises:
            NotImplementedError: If other is not a Task.
        """
        if not isinstance(other, Task):
            return NotImplemented
        eq = self.train == other.train and self.test == other.test
        if eq and self.task_id != other.task_id:
            warnings.warn(
                "train and test pairs are the same but task_id is different. Equality does not rely on task_id but you might want to have their task_id same since their composition(train, test pairs) are the same. ",
                UserWarning,
                stacklevel=2,
            )
        if not eq and self.task_id == other.task_id:
            warnings.warn(
                "train and test pairs are not the same but task_id is the same. Equality does not rely on task_id but you might want to have their task_id different since their composition(train, test pairs) are not the same. ",
                UserWarning,
                stacklevel=2,
            )
        return eq

    def __hash__(self) -> int:
        """
        Compute a hash of the Task based on train and test pairs.

        Returns:
            int: Hash value.
        """
        return abs(hash((tuple(self.train), tuple(self.test))))

    def __copy__(self) -> Self:
        """
        Create a shallow copy of the Task.

        Returns:
            Task: Shallow copy of the Task.
        """
        return type(self)(self.train, self.test, self.task_id)

    def __deepcopy__(self, memo) -> Self:
        """
        Create a deep copy of the Task.

        Args:
            memo (dict): Memoization dictionary for deepcopy.

        Returns:
            Task: Deep copy of the Task.
        """
        return type(self)(
            deepcopy(self.train, memo), deepcopy(self.test, memo), self.task_id
        )

    @classmethod
    def random(cls) -> Self:
        """
        Generate a random Task instance.

        Both the training and test sets will contain random Pair instances.
        The number of training pairs will be between 2 and 5 (inclusive),
        and the number of test pairs will be between 1 and 3 (inclusive).

        Returns:
            Task: A randomly generated Task instance.
        """
        return cls(
            [Pair.random() for _ in range(random.randint(2, 5))],
            [Pair.random() for _ in range(random.randint(1, 3))],
        )
