import abc
from typing import Union, List, Dict, Iterator, Self, Literal, overload
from pathlib import Path
from ._task import Task
import warnings
from ._utils import download_from_github
import json
from ._errors import ArcError
import random


class Dataset(abc.ABC):
    """
    Base class for ARC dataset.

    This class provides a framework for managing collections of ARC tasks stored as JSON files.
    It supports lazy loading, task lookup by index or ID, and iteration. Subclasses must implement
    the download() method to fetch the dataset from a remote source.

    Methods:
        download(): Download the dataset (to be implemented by subclasses).
        __len__(): Return the number of tasks in the dataset.
        __contains__(task_id): Check if a task ID exists in the dataset.
        __getitem__(key): Retrieve a Task by index (int) or by task_id (str), lazy loading.
        load_all(): Load all tasks into memory.
        __iter__(): Iterate over all tasks in the dataset.
    """

    def __init__(
        self,
        path: Union[str, Path],
        split: Literal["training", "evaluation"],
        download: bool = True,
    ):
        """
        Initializes the dataset for lazy loading.

        Args:
            path (str | Path): Path to the dataset directory.
            split ("training" | "evaluation"): Which split the dataset is.
            download (bool): Whether to download the dataset if not present (default: True).
        """
        if split not in ("training", "evaluation"):
            raise ArcError(
                f'Split should be either "training" or "evalaution" but given {split}'
            )
        self._split = split

        self._path = Path(path)

        if download:
            self.download()

        self._files: List[Path] = sorted(self._path.glob("*.json"))
        if not self._files:
            raise ArcError(f"No .json files found in {self._path}")

        self._id_to_idx: Dict[str, int] = {
            path.stem: i for i, path in enumerate(self._files)
        }
        self._cache: Dict[int, Task] = {}
        self._indices: List[int] = list(range(len(self._files)))

    @abc.abstractmethod
    def download(self) -> None:
        """
        Downloads the dataset. To be implemented by subclasses.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError("Subclasses must implement the download method.")

    def __len__(self) -> int:
        """
        Returns the number of tasks in the dataset.

        Returns:
            int: Number of tasks.
        """
        return len(self._indices)

    def __contains__(self, task_id: str) -> bool:
        """
        Checks if a task with the given ID exists in the dataset.

        Args:
            task_id (str): The task ID to check.

        Returns:
            bool: True if the task exists, False otherwise.
        """
        return task_id in self._id_to_idx

    @overload
    def __getitem__(self, key: Union[int, str]) -> Task: ...

    @overload
    def __getitem__(self, key: slice) -> Self: ...

    def __getitem__(self, key: Union[int, str, slice]) -> Union[Task, Self]:
        """
        Retrieves a task by its index (int) or by its task_id (str), loading it lazily.

        Args:
            key (int | str): Index of the task or task ID.

        Returns:
            Task: The loaded Task object.

        Raises:
            ArcError: If the index or task ID is invalid, or if the key type is unsupported.
        """
        if isinstance(key, int):
            if not 0 <= key < len(self._files):
                raise ArcError(
                    f"Index {key} out of range for dataset of length {len(self._files)}."
                )
            index = self._indices[key]
        elif isinstance(key, str):
            if key not in self._id_to_idx:
                raise ArcError(f"Task with task id: {key} is not in this dataset.")
            index = self._id_to_idx[key]
        elif isinstance(key, slice):
            return self._from_indices(self._indices[key])
        else:
            raise ArcError("Key must be int (index) or str (task_id)")

        if index not in self._cache:
            file_path = self._files[index]
            try:
                task = Task.load_json(file_path)
                self._cache[index] = task
            except json.JSONDecodeError as e:
                warnings.warn(
                    f"Error parsing JSON from '{file_path}': {e}", RuntimeWarning
                )
            except ValueError as e:
                warnings.warn(
                    f"Error loading task from '{file_path}': {e}", RuntimeWarning
                )
            except Exception as e:
                warnings.warn(
                    f"Unexpected error loading task from '{file_path}': {e}",
                    RuntimeWarning,
                )
        return self._cache[index]

    def load_all(self) -> None:
        """
        Eagerly load all tasks in the dataset into cache.
        """
        for i in range(len(self)):
            _ = self[i]  # Trigger lazy loading for all tasks

    def __repr__(self) -> str:
        return f"<Dataset> task #: {len(self)} | split: {self._split}"

    def __iter__(self) -> Iterator[Task]:
        """
        Iterates over the tasks in the dataset, loading them lazily.

        Yields:
            Task: Each Task object in the dataset.
        """
        for i in range(len(self)):
            yield self[i]

    def _from_indices(self, indices: List[int]) -> Self:
        obj = self.__class__.__new__(self.__class__)
        obj._path = self._path
        obj._id_to_idx = {
            id: idx for id, idx in self._id_to_idx.items() if idx in indices
        }
        obj._files = [path for path in self._files if path.stem in obj._id_to_idx]
        obj._cache = {idx: task for idx, task in self._cache.items() if idx in indices}
        obj._indices = indices
        obj._split = self._split
        return obj

    @overload
    def sample(self, k: Literal[1] = 1) -> Task: ...

    @overload
    def sample(self, k: int) -> Self: ...

    def sample(self, k: int = 1) -> Union[Task, Self]:
        picked = random.sample(self._indices, k)
        return self[picked[0]] if k == 1 else self._from_indices(picked)

    def shuffle(self) -> Self:
        """
        Returns a new Dataset instance with the tasks shuffled.

        The underlying files and cache are not modified in-place; instead, a new Dataset
        object is returned with a shuffled order of indices.

        Returns:
            Self: A new Dataset instance with shuffled task order.
        """
        shuffled_indices = self._indices.copy()
        random.shuffle(shuffled_indices)
        return self._from_indices(shuffled_indices)

    def select(self, task_ids: List[str]) -> Self:
        missing = set(task_ids) - self._id_to_idx.keys()
        if missing:
            raise ArcError(f"Unknown task_id: {', '.join(missing)}")
        indices = [self._id_to_idx[task_id] for task_id in task_ids]
        return self._from_indices(indices)

    def to_list(self) -> List[Task]:
        self.load_all()
        return list(self._cache.values())

    def __setitem__(self, key: Union[int, str], value: Task) -> None:
        """
        Sets a Task in the dataset cache by index or task_id.

        Args:
            key (int | str): Index or task_id to set.
            value (Task): The Task object to store.

        Raises:
            ArcError: If the key is invalid or out of range.
            TypeError: If value is not a Task.
        """
        if not isinstance(value, Task):
            raise ArcError("Value must be a Task instance.")

        if isinstance(key, int):
            if not 0 <= key < len(self._files):
                raise ArcError(
                    f"Index {key} out of range for dataset of length {len(self._files)}."
                )
            index = key
        elif isinstance(key, str):
            if key not in self._id_to_idx:
                raise ArcError(f"Task with task id: {key} is not in this dataset.")
            index = self._id_to_idx[key]
        else:
            raise ArcError("Key must be int (index) or str (task_id)")

        self._cache[index] = value


class ARC1(Dataset):
    """
    Represents the ARC1 dataset.

    Downloads and manages the original ARC dataset from François Chollet's ARC-AGI repository.
    """

    def download(self) -> None:
        """
        Downloads the ARC1 dataset from GitHub.

        Downloads either the training or evaluation split, depending on the 'train' flag.
        """
        download_from_github(
            "fchollet", "ARC-AGI", f"data/{self._split}", "master", self._path
        )


class ARC2(Dataset):
    """
    Represents the ARC2 dataset, inheriting functionality from Dataset.

    Downloads and manages the ARC-AGI-2 dataset from the arcprize organization.
    """

    def download(self) -> None:
        """
        Downloads the ARC2 dataset from GitHub.

        Downloads either the training or evaluation split, depending on the 'train' flag.
        """
        download_from_github(
            "arcprize", "ARC-AGI-2", f"data/{self._split}", "main", self._path
        )
