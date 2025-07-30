"""Module for user input utility functions."""

import sys
import json
from typing import Any


def query_yes_no(question: str, default: str = "no") -> bool:
    """Ask a yes/no question via raw_input() and return their answer.

    Args:
        question: A string that is presented to the user.
        default: The presumed answer if the user just hits <Enter>.\
                It must be "yes", "no" or None (meaning an answer is required of\
                the user). (default: "no")

    Returns:
        The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError(f"invalid default answer: '{default}'")

    while True:
        sys.stdout.write(question + prompt)
        # pylint: disable=bad-builtin
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        if choice in valid:
            return valid[choice]
        sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def dict_from_json_file(path) -> Any:
    """Reads a JSON file from the given `path` and returns its contents as a dictionary.

    Args:
        path (str): The path to the JSON file.

    Returns:
        dict or None: The contents of the JSON file as a dictionary or None if the given `path` is None.

    Raises:
        FileNotFoundError: If the file at the given `path` does not exist.

    Examples:

    Convert the contents of a JSON file to a dictionary:
    >>> import os
    >>> dict_from_json_file(os.path.join("tests","documents","example.json"))
    {'name': 'John', 'age': 30, 'city': 'New York'}

    Raise an error if the file does not exist:
    >>> dict_from_json_file("non_existent_file.json")
    Traceback (most recent call last):
        ...
    FileNotFoundError: [Errno 2] No such file or directory: 'non_existent_file.json'
    """
    if path is None:
        return None
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            raise FileNotFoundError(e) from e
