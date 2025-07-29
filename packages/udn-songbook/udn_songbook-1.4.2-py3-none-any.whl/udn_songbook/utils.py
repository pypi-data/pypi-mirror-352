"""Utility functions that aren't really class-specific."""
# vim: set ft=python:

import logging
import os
import re
from string import punctuation


def make_dir(destdir: str, logger: logging.Logger | None):
    """Attempt to create a directory if it doesn't already exist.

    Raise an error if the creation fails
    """
    if os.path.exists(destdir):
        return True
    else:
        try:
            os.makedirs(destdir)
            return True
        except OSError as E:
            if logger:
                logger.exception(
                    f"Unable to create output dir {E.filename} - {E.strerror}"
                )
            raise


def unpunctuate(name: str, replacement: str = "") -> str:
    """Remove punctuation from the given name.

    Simply removes punctuation from the given name, for ease of sorting.

    Args:
        name(str): the name you want to unpunctuate
        replacement(str): what to replace punctuation with.
    """
    TRANS = {ord(char): replacement for char in punctuation}
    return name.translate(TRANS)


def safe_filename(filename: str) -> str:
    """Remove UNIX-unfriendly characters from filenames.

    Just simple string translation to remove UNIX-unfriendly characters from filenames
    removes the following characters from filenames:

    """
    tt = {ord(char): "_" for char in punctuation if char not in ["#", "-", "_", "."]}
    # this replaces '#' though, so escape that.
    tt.update({ord("#"): "_sharp_"})

    return re.sub(r"_+", r"_", filename.translate(tt))
