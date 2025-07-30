from __future__ import annotations

from typing import (
    Sequence,
    Dict,
    List,
    Union,
    Self,
    overload,
    Optional,
    Iterator,
    Literal,
)
from pathlib import Path
import random
from ._grid import Grid
from ._pair import Pair
from ._task import Task
from ._errors import ArcError
from ._utils import download_from_github, Link
from copy import copy, deepcopy
from abc import ABC, abstractmethod
import json


class Dataset:
    """
    Represents a collection of ARC tasks, allowing for lazy loading and easy access.

    A Dataset can be initialized with a sequence of Task objects or loaded from a
    directory containing task JSON files. Tasks are loaded into memory only when
    accessed, improving performance for large datasets.

    Methods:
        load_directory(path): Creates a Dataset by loading task IDs from a directory.
        select(keys): Creates a new Dataset containing a subset of tasks.
        sample(k): Returns one or more random tasks from the dataset.
        shuffle(): Returns a new Dataset with tasks in a random order.
        to_list(): Returns a list of all Task objects in the dataset.
        cache_all(): Eagerly loads all tasks into the cache.
        __len__(): Returns the number of tasks in the dataset.
        __contains__(key): Checks if a task exists in the dataset.
        __getitem__(key): Retrieves a task by index, task_id, or slice.
        __setitem__(key, value): Sets a Task in the dataset cache.
        __copy__(): Creates a shallow copy of the Dataset.
        __deepcopy__(memo): Creates a deep copy of the Dataset.
        __repr__(): Returns a string representation of the Dataset.
        __iter__(): Iterates over the tasks in the dataset.
        __eq__(other): Checks for equality with another Dataset.
        __hash__(): Computes a hash value for the Dataset.
        __str__(): Returns a string representation of the Dataset.
        __add__(other): Concatenates this dataset with another Dataset, Task, or sequence of Tasks.
        __iadd__(other): In-place concatenation of this dataset with another Dataset, Task, or sequence of Tasks.
    """

    def __init__(self, tasks: Optional[Sequence[Task]] = None) -> None:
        """Initializes a Dataset instance.

        Args:
            tasks (Optional[Sequence[Task]]): An optional sequence of Task objects to populate the dataset.
                                            If None, an empty dataset is created.

        Raises:
            TypeError: If any element in `tasks` is not an instance of `Task`.
        """
        if tasks is not None:
            for task in tasks:
                if not isinstance(task, Task):
                    raise TypeError(f"Unsupported type: {type(task)}")
        self._path: Optional[Path] = None
        self._task_ids: List[str] = [task.task_id for task in tasks] if tasks else []
        self._cache: Dict[str, Optional[Task]] = (
            {task.task_id: task for task in tasks} if tasks else {}
        )

    @classmethod
    def load_directory(cls, path: Union[str, Path]) -> Self:
        """
        Creates a Dataset by discovering task JSON files in the specified directory.

        Args:
            path (Union[str, Path]): The path to the directory containing task JSON files.
                                     Each .json file is assumed to be a task, with its
                                     stem as the task_id.
        Returns:
            Self: A new Dataset instance populated with task IDs from the directory.
        """
        dataset = cls()
        dataset._path = Path(path)
        dataset._task_ids = [
            task_file.stem for task_file in dataset._path.glob("*.json")
        ]
        dataset._cache = {task_id: None for task_id in dataset._task_ids}
        return dataset

    def save_directory(self, path: Union[str, Path], git_ignore: bool = True) -> Link:
        """
        Saves the dataset to a directory.

        Args:
            path (Union[str, Path]): The path to the directory where the dataset will be saved.
            git_ignore (bool): If True, creates a .gitignore file in the `path` directory
                               to ignore *.json files. Defaults to True.
        Returns:
            Link: Link to the saved directory.
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        for task_id in self._task_ids:
            self[task_id].save_json(path / f"{task_id}.json")
        if git_ignore:
            (path / ".gitignore").write_text("*.json")
        return Link(path)

    def to_dict(
        self,
    ) -> Dict[str, Dict[str, List[Dict[str, Optional[List[List[int]]]]]]]:
        """
        Converts the dataset to a dictionary representation.

        Returns:
            Dict[str, Dict[str, List[Dict[str, Optional[List[List[int]]]]]]]: Dictionary mapping task_id to its dictionary representation.
        """
        return {task.task_id: task.to_dict() for task in self}

    def to_json(self) -> str:
        """
        Converts the dataset to a single JSON string.

        Returns:
            str: A JSON string representing the dataset.
        """
        return json.dumps(self.to_dict())

    def save_json(self, path: Union[str, Path]) -> Link:
        """
        Saves the dataset to a single JSON file.

        Args:
            path (Union[str, Path]): The path to the JSON file where the dataset will be saved.

        Returns:
            Link: Link to the saved JSON file.
        """
        path = Path(path)
        try:
            if path.suffix != ".json":
                path = path.with_suffix(".json")
            path.write_text(self.to_json())
            return Link(path)
        except IOError as e:
            raise IOError(f"Error saving Dataset to JSON '{path}': {e}") from e

    @classmethod
    def load_json(cls, path: Union[str, Path]) -> Self:
        """
        Loads a Dataset from a single JSON file.

        Args:
            path (Union[str, Path]): The path to the JSON file containing the dataset.

        Returns:
            Self: A new Dataset instance loaded from the JSON file.
        """
        path = Path(path)
        try:
            data = json.loads(path.read_text())
            tasks = [
                Task(
                    [
                        Pair(pair["input"], pair.get("output", None))
                        for pair in task_data["train"]
                    ],
                    [
                        Pair(pair["input"], pair.get("output", None))
                        for pair in task_data["test"]
                    ],
                    task_id=task_id,
                )
                for task_id, task_data in data.items()
            ]
            return cls(tasks)
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Error loading Dataset from JSON '{path}': {e}") from e

    @property
    def challenges(self) -> Self:
        """
        Dataset consisting of only challenges.
        """
        return type(self)([task.challenge for task in self])

    @property
    def solutions(self) -> Dict[str, List[Grid]]:
        """
        Provides a dictionary mapping task IDs to a list of the *uncensored*
        output grids from their test pairs.

        Note that this property will only return non-None grids. If a test pair's
        output is still censored, it will be excluded from the list for that task.

        Returns:
            Dict[str, List[Grid]]: A dictionary mapping task_id to its test solutions.
        """
        return {task.task_id: task.solution for task in self}

    def __len__(self) -> int:
        """
        Returns the number of tasks in the dataset.

        Returns:
            int: The total number of tasks.
        """
        return len(self._task_ids)

    def __contains__(self, key: Union[int, str]) -> bool:
        """
        Checks if a task exists in the dataset by index or task_id.

        Args:
            key (Union[int, str]): The index or task_id to check.

        Returns:
            bool: True if the task exists, False otherwise.
        """
        if isinstance(key, int):
            return 0 <= key < len(self)
        elif isinstance(key, str):
            return key in self._task_ids
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")

    @overload
    def __getitem__(self, key: Union[int, str]) -> Task: ...

    @overload
    def __getitem__(self, key: slice) -> Self: ...

    def __getitem__(self, key: Union[int, str, slice]) -> Union[Task, Self]:
        """
        Retrieves a task by its index or task_id, or a new Dataset by slice.

        Tasks are loaded lazily from disk if not already cached.

        Args:
            key (Union[int, str, slice]): The index (int), task_id (str), or slice to retrieve.

        Returns:
            Union[Task, Self]: The requested Task object if key is int or str,
                               or a new Dataset instance if key is a slice.
        Raises:
            ArcError: If the index or task_id is invalid.
            TypeError: If the key type is unsupported.
        """
        if isinstance(key, int):
            if key not in self:
                raise ArcError(
                    f"Index {key} out of range for dataset of length {len(self)}."
                )
            task_id = self._task_ids[key]
        elif isinstance(key, str):
            if key not in self:
                raise ArcError(f"Task with task id: {key} is not in this dataset.")
            task_id = key
        elif isinstance(key, slice):
            return self.select(key)
        else:
            raise TypeError("Key must be int (index), str (task_id), or slice")

        cached_task = self._cache[task_id]
        if cached_task is None:
            if self._path is None:
                raise ArcError("Dataset path not set.")
            task_file_path = self._path / f"{task_id}.json"
            try:
                task = Task.load_json(task_file_path)
                cached_task = task
                self._cache[task_id] = cached_task
            except Exception as e:
                raise ArcError(
                    f"Unexpected error loading task from '{task_file_path}': {e}"
                )
        return copy(cached_task)

    def __setitem__(self, key: Union[int, str], value: Task) -> None:
        """
        Sets a Task in the dataset cache by index or task_id.

        Args:
            key (int | str): Index or task_id to set.
            value (Task): The Task object to store.
                               The task_id of the value will replace the existing task_id at the index if key is an int.

        Raises:
            ArcError: If the key is invalid or out of range, or if value is not a Task.
        """
        if not isinstance(value, Task):
            raise ArcError("Value must be a Task instance.")
        if key not in self:
            raise ArcError(f"Task with task id: {key} is not in this dataset.")
        if isinstance(key, int):
            self._task_ids[key] = value.task_id
            if key != self._task_ids.index(value.task_id):
                self._cache.pop(self._task_ids[key])
            self._cache[value.task_id] = value
        elif isinstance(key, str):
            self._cache[key] = value

    def __copy__(self) -> Self:
        """
        Creates a shallow copy of the Dataset.

        Returns:
            Self: A new Dataset instance with copied task_ids and a shallow copy of the cache.
        """
        dataset = type(self)()
        dataset._path = self._path
        dataset._task_ids = self._task_ids.copy()
        dataset._cache = {
            task_id: copy(self._cache[task_id]) for task_id in self._task_ids
        }
        return dataset

    def __deepcopy__(self, memo) -> Self:
        """
        Creates a deep copy of the Dataset.

        Args:
            memo (dict): Memoization dictionary for deepcopy.

        Returns:
            Self: A new Dataset instance with copied task_ids and a deep copy of the cache.
        """
        dataset = type(self)()
        dataset._path = self._path
        dataset._task_ids = self._task_ids.copy()
        dataset._cache = {
            task_id: deepcopy(self._cache[task_id], memo) for task_id in self._task_ids
        }
        return dataset

    def select(self, keys: Union[Sequence[Union[int, str]], slice]) -> Self:
        """
        Creates a new Dataset containing a subset of tasks specified by keys or a slice.

        The new dataset shares the same path and cache entries (shallow copy) for
        the selected tasks.

        Args:
            keys (Union[Sequence[Union[int, str]], slice]): A sequence of task indices (int)
                or task_ids (str), or a slice object.

        Returns:
            Self: A new Dataset instance containing only the selected tasks.
        """
        dataset = type(self)()
        dataset._path = self._path
        if isinstance(keys, slice):
            dataset._task_ids = self._task_ids[keys]
        elif isinstance(keys, Sequence):
            for key in keys:
                if key not in self:
                    raise ArcError(f"Task with task id: {key} is not in this dataset.")
            dataset._task_ids = [
                self._task_ids[key] if isinstance(key, int) else key for key in keys
            ]
        else:
            raise TypeError(f"Unsupported key type: {type(keys)}")
        dataset._cache = {
            task_id: copy(self._cache[task_id]) for task_id in dataset._task_ids
        }
        return dataset

    def __repr__(self) -> str:
        """
        Returns a string representation of the Dataset.

        Returns:
            str: A string showing the type and number of tasks.
        """
        return f"<Dataset: {len(self)} tasks>"

    def __iter__(self) -> Iterator[Task]:
        """
        Iterates over the tasks in the dataset, loading them lazily.

        Yields:
            Task: Each Task object in the dataset.
        """
        for i in range(len(self)):
            yield self[i]

    @overload
    def sample(self, k: Literal[1] = 1) -> Task: ...

    @overload
    def sample(self, k: int) -> Self: ...

    def sample(self, k: int = 1) -> Union[Task, Self]:
        """
        Returns one or more random tasks from the dataset.

        Args:
            k (int): The number of tasks to sample. Defaults to 1.

        Returns:
            Union[Task, Self]: A single Task if k is 1, otherwise a new Dataset
                               containing k randomly selected tasks.
        """
        picked = random.sample(self._task_ids, k)
        return self[picked[0]] if k == 1 else self.select(picked)

    def shuffle(self) -> Self:
        """
        Returns a new Dataset instance with the task order shuffled.

        The underlying files and cache are not modified in-place; instead, a new Dataset
        object is returned with a shuffled order of indices.

        Returns:
            Self: A new Dataset instance with shuffled task order.
        """
        shuffled_indices = self._task_ids.copy()
        random.shuffle(shuffled_indices)
        return self.select(shuffled_indices)

    def to_list(self) -> List[Task]:
        """
        Converts the dataset to a list of Task objects.

        This will load all tasks into memory if they haven't been loaded already.

        Returns:
            List[Task]: A list containing all Task objects in the dataset.
        """
        return [self[i] for i in range(len(self))]

    def cache_all(self) -> Self:
        """
        Loads all tasks in the dataset into the cache.

        This method eagerly loads all the tasks into in-memory cache.

        Returns:
        Self: The Dataset instance, with all tasks now cached.
        """
        for i in range(len(self)):
            self[i]
        return self

    def __add__(self, other: object) -> Self:
        """
        Concatenates this dataset with another Dataset, Task, or sequence of Tasks.

        Args:
            other (object): Another Dataset, a single Task, or a sequence of Tasks.

        Returns:
            Self: A new Dataset instance containing tasks from both operands.
                  Duplicate task_ids are preserved based on their first appearance.
        """
        if isinstance(other, Dataset):
            dataset = type(self)()
            dataset._path = self._path if self._path == other._path else None
            dataset._task_ids = list(dict.fromkeys(self._task_ids + other._task_ids))
            dataset._cache = {
                task_id: self._cache[task_id]
                if task_id in self._cache
                else other._cache[task_id]
                for task_id in dataset._task_ids
            }
            return dataset
        elif isinstance(other, Task):
            if other.task_id in self._task_ids:
                return self
            dataset = copy(self)
            dataset._task_ids.append(other.task_id)
            dataset._cache[other.task_id] = other
            return dataset
        elif isinstance(other, Sequence):
            return self.__add__(Dataset(other))
        else:
            raise TypeError(f"Unsupported type: {type(other)}")

    def __iadd__(self, other: object) -> Self:
        """
        In-place concatenation of this dataset with another Dataset, Task, or sequence of Tasks.

        Args:
            other (object): Another Dataset, a single Task, or a sequence of Tasks.

        Returns:
            Self: The current Dataset instance, modified to include tasks from the other operand.
                  Duplicate task_ids are preserved based on their first appearance.
        """
        if isinstance(other, Dataset):
            self._path = self._path if self._path == other._path else None
            self._task_ids = list(dict.fromkeys(self._task_ids + other._task_ids))
            self._cache = {
                task_id: self._cache[task_id]
                if task_id in self._cache
                else other._cache[task_id]
                for task_id in self._task_ids
            }
        elif isinstance(other, Task):
            if other.task_id in self._task_ids:
                return self
            self._task_ids.append(other.task_id)
            self._cache[other.task_id] = other
        elif isinstance(other, Sequence):
            return self.__iadd__(Dataset(other))
        else:
            raise TypeError(f"Unsupported type: {type(other)}")
        return self


class RemoteDataset(Dataset, ABC):
    """
    Abstract base class for datasets that can be downloaded from a remote source.

    Subclasses must implement the `fetch_from_remote_source` method to define
    how the dataset files are obtained.
    """

    @classmethod
    def download(cls, path: Union[str, Path], git_ignore: bool = True) -> Self:
        """
        Downloads the dataset from its remote source and loads it.

        Args:
            path (Union[str, Path]): The local directory path to download and store the dataset.
            git_ignore (bool): If True, creates a .gitignore file in the `path` directory
                               to ignore *.json files. Defaults to True.
        Returns:
            Self: A Dataset instance loaded from the downloaded files.
        """
        dataset = cls()
        dataset.fetch_from_remote_source(path)
        if git_ignore:
            try:
                (Path(path) / ".gitignore").write_text("*.json")
            except Exception as e:
                ArcError(f"Failed to create .gitignore: {e}")
        dataset = cls.load_directory(path)
        return dataset

    @classmethod
    @abstractmethod
    def fetch_from_remote_source(cls, path: Union[str, Path]) -> None:
        """
        Abstract method to fetch dataset files from a remote source.

        Subclasses must implement this to specify the download logic.

        Args:
            path (Union[str, Path]): The local directory path to save the downloaded files.
        """
        raise NotImplementedError("Subclasses must implement the download method.")


class ARC1Training(RemoteDataset):
    """
    Represents the ARC-1 (ARC-AGI v1) training dataset.

    Provides a method to download the dataset from the official fchollet/ARC-AGI GitHub repository.
    """

    @classmethod
    def fetch_from_remote_source(cls, path: Union[str, Path]) -> None:
        """
        Downloads the ARC-1 training dataset files from GitHub.

        Args:
            path (Union[str, Path]): The local directory path to save the downloaded files.
        """
        download_from_github("fchollet", "ARC-AGI", "data/training", "master", path)


class ARC1Evaluation(RemoteDataset):
    """
    Represents the ARC-1 (ARC-AGI v1) evaluation dataset.

    Provides a method to download the dataset from the official fchollet/ARC-AGI GitHub repository.
    """

    @classmethod
    def fetch_from_remote_source(cls, path: Union[str, Path]) -> None:
        """
        Downloads the ARC-1 evaluation dataset files from GitHub.

        Args:
            path (Union[str, Path]): The local directory path to save the downloaded files.
        """
        download_from_github("fchollet", "ARC-AGI", "data/evaluation", "master", path)


class ARC2Training(RemoteDataset):
    """
    Represents the ARC-2 (ARC Prize 2024) training dataset.

    Provides a method to download the dataset from the official arcprize/ARC-AGI-2 GitHub repository.
    """

    @classmethod
    def fetch_from_remote_source(cls, path: Union[str, Path]) -> None:
        """
        Downloads the ARC-2 training dataset files from GitHub.

        Args:
            path (Union[str, Path]): The local directory path to save the downloaded files.
        """
        download_from_github("arcprize", "ARC-AGI-2", "data/training", "main", path)


class ARC2Evaluation(RemoteDataset):
    """
    Represents the ARC-2 (ARC Prize 2024) evaluation dataset.

    Provides a method to download the dataset from the official arcprize/ARC-AGI-2 GitHub repository.
    """

    @classmethod
    def fetch_from_remote_source(cls, path: Union[str, Path]) -> None:
        """
        Downloads the ARC-2 evaluation dataset files from GitHub.

        Args:
            path (Union[str, Path]): The local directory path to save the downloaded files.
        """
        download_from_github("arcprize", "ARC-AGI-2", "data/evaluation", "main", path)
