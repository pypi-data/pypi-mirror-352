#!/usr/bin/env python3
# vim: set ts=4 sts=4 sw=4 et ci nu ft=python:
"""Class representing a songbook."""

import fnmatch

# from jinja2 import Environment, FileSystemLoader
import logging
import os
from collections import OrderedDict
from operator import itemgetter
from pathlib import Path
from typing import Optional, Union

from udn_songbook import song

from .config import settings

# from glob import glob


class SongBook:
    """Wrapper class representing a songbook.

    A songbook is essentially an indexed list of Song objects, generated from
    UDN-formatted files Songs are indeced on Title and Artist

    Duplicate title/artist combinations are not supported - if you add more
    than one song with the same Title & Artist, the last one seen will win.
    Order matters.
    """

    def __init__(
        self,
        inputs: list[str] = [],
        logger: Union[logging.Logger, None] = None,
        template_paths: list[str] = [],
        song_template: str = "song.html.j2",
        index_template: str = "index.html.j2",
        title: str = "My Songbook",
        profile: Optional[str] = None,
        style: Path | list[Path] = [],
    ):
        """Create a songbook object from a list of inputs.

        Inputs can be directories, too.

        Songs in a book are indexed on 'Title - Artist', which is parsed out of
        the ukedown markup. Duplicate index entries are not supported.
        If 2 songs are added with the same Title and Artist, the last one wins

        Template locations and filenames can be provided - there are defaults (included
        in the package). The default names are in the function signature. Any templates
        provided as arguments override the packaged ones.

        CSS stylesheet filenames (as pathlib.Path objects) may be provided. If the
        stylesheets depend on one another (as the default packaged ones do), then you
        should provide them all as arguments.

        Args:
            inputs( list[str]):   list of files or directories containing UDN files
            logger (logging.Logger | None): where to log messages to.
            template_paths (str): Paths to jinja2 template directories.
            song_template (str):  filename of jinja2 template for rendering Song objects
            index_template (str): filename of jinja2 template for rendering the index.

            title (str):          a title for the songbook, for use in templates
            style (Path | list[Path]):     CSS stylesheet

        # to be added /managed, probably via dynaconf
        #    config(str):        filename for CSS and other configuration
        """
        if not isinstance(inputs, list):
            self._inputs = [inputs]
        else:
            self._inputs = inputs
        # keep track of all the chord diagrams we need for the book
        # these are no longer strings, so `chords` can no longer be a set.
        self.chords = []
        self.contents = []
        # index will actually be { 'title - artist' : song object }
        self._index = OrderedDict()
        self.song_template = song_template
        self.index_template = index_template
        self.template_paths = template_paths
        self._title = title
        self._style = style
        self._styles_dir = Path(__file__).parent / "stylesheets"
        self.settings = settings

        # logger instance, if there is one.
        self._logger = logger
        if len(self._inputs):
            self.populate()
            self.renumber()

    def __log(self, message: str, prio: int = logging.DEBUG, **kwargs):
        """Emit a log message, or don't, if self.logger is None.

        presumes that self.logger is a logging.Logger instance
        with configured handlers, formats etc. No attempt is made to do
        this part for you

        Args:
            message(str): the message to emit
        KWargs:
            prio(int): the priority of the message. Default is 10 (logging.DEBUG)

        You may also provide other kwargs supported by the logger.log method
        """
        if self._logger is not None:
            self._logger.log(prio, message, **kwargs)
        else:
            return

    def add_song(self, path: str):
        """Add a song to the contents list and index.

        Args:
            songdata(str): path to a file (usually)
        """
        try:
            s = song.Song(path, template=self.song_template)
            # add the song object to our content list
            self.contents.append(s)
            # add the chords it uses to our chords list
            self.chords.extend([c for c in s.chords if c not in self.chords])
            # insert into index
            self._index[s.songid] = s
            self.__log(f"Added {path} with id {s.songid}")
        except Exception:
            print("failed to add song", path)
            self.__log(f"failed to add {path}", logging.ERROR, exc_info=True)
            raise

    def populate(self):
        """Read in the content of any input directories, as Song objects."""
        for src in self._inputs:
            if os.path.exists(src):
                rp = os.path.realpath(src)
                if os.path.isfile(rp) and fnmatch.fnmatch(
                    os.path.basename(rp), "*.udn"
                ):
                    self.__log(f"adding songfile {rp}")
                    self.add_song(rp)
                    continue
                if os.path.isdir(rp):
                    self.__log(f"Scanning dir {rp} for ukedown files")
                    for rt, _, files in os.walk(rp):
                        for f in fnmatch.filter(
                            [os.path.join(rt, f) for f in files], "*.udn"
                        ):
                            self.add_song(f)
            else:
                self.__log(f"cannot load from non-file/dir {src}", logging.ERROR)

    def collate(self):
        """Reduce contents list to unique entries, indexed on title - artist.

        title and artist must be a unique combination.
        Although we could permit dupes I guess, depending on the book.
        """
        self._index = OrderedDict(
            {k: v for (k, v) in sorted(self._index.items(), key=itemgetter(0))}
        )

    def renumber(self):
        """Renumber pages in a collated book."""
        self.collate()
        for i, k in enumerate(self._index):
            self._index[k].id = i

    def update(self, inputs: list[str]):
        """Replace entries in an existing songbook using the provided inputs.

        This will regenerate the index
        """
        self.inputs.append(inputs)
        self.populate()
        self.renumber()

    def refresh(self):
        """Reload all the current inputs (that have changed).

        This will be a timestamp/checksumming/stat operation when I've
        written that part
        """
        # this is a PATH operation and will rebuild the songbook index
        # this permits us to change metadata (title etc) and have the book
        # reordered appropriately.
        if len(self._inputs):
            self.populate()
            self.renumber()

    def publish(self, publisher_class, *args, **kwargs):
        """Render the entire book.

        Steps:
        1. creating an output structure
        2. rendering the files
        3. generating a index page

        """
        self.publisher = publisher_class(*args, **kwargs)

        self.publisher.publish()

    @property
    def inputs(self):
        """Show the inputs used to build the book."""
        return self._inputs

    @property
    def index(self):
        """Show the generated index."""
        return self._index

    @property
    def title(self):
        """Show the book title."""
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title

    @property
    def styles_dir(self):
        """Show where our CSS files are."""
        return self._styles_dir

    @styles_dir.setter
    def styles_dir(self, data: Path):
        if data.is_dir():
            self._styles_dir = data
        else:
            raise ValueError(
                "styles_dir must be a Path object, pointing to a directory"
            )

    @property
    def style(self):
        """Show the primary stylesheet in use."""
        return self._style

    @style.setter
    def style(self, data: Path | list[Path]):
        if isinstance(data, Path):
            self._style = [data]
        else:
            self._style = data
