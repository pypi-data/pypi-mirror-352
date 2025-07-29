# CHANGELOG for udn_songbook

This project attempts to adhere to [semantic versioning](https://semver.org)
## 1.3.0
- Add dynaconf and profile support
- Docstrings everywhere
- move to pathlib whereever possible
- move to f-strings rather than str.format


## 1.2.0
- Add support for singers notes to template
- Add style (.singer) for singers' notes
- Docstringi, type hints and other linting updates
- Switch to ruff for python pre-commit, update versions
- remove unhelpful self._filename override
- Force normal font-style on elements inside backing vox

## 1.1.8

- Fix template for index generation
- Add latest CSS from ukebook-md
- Fix singers options in makesheet
- Unpunctuate song._index_entry for better sorting
- Rename default stylesheet to 'portrait.css'

## 1.1.7

- README updated with new udn_songbook.Song features

- BUGFIX: default metadata to empty dict if not present in songsheet
- BUGFIX: use absolute import for Song in transpose.py

## 1.1.6

- Adds README to project files for PyPi

## 1.1.5

- rename udn_render to udn_songsheet (script entry point)
- BUGFIX: stop wiping metadata after parsing songsheets

## 1.1.4

- support more than 100 songs in a songbook
- move tools into `udn_songbook/tools`
- new rendering tool
- update templates to support standalone songsheets (no footer links)
- BUGFIX: transpose no longer removes content after last chord.


## 1.1.3

- add scripts to project files
- add PDF rendering code
- move to pathlib.Path for filenames
- add `udn_transpose` entry point for transposing tool
- UNIX-safe chordnames
- template support for pychord.Chord objects

## 1.1.2

- dependency and documentation updates
- add license


## 1.1.1

- more sane boolean template vars
- new kwargs for templates (song & index)
- updated dependencies (new versions of blck/click/weasyprint etc)

## 1.1.0

- add page IDs
- adds rendering code & template for songs
- use pychord for chord naming
- add transposition code using pychord
- fix chord parsing to handle 'tails' like '*'
- page numbering and content deduplication

## 1.0.4

- require python >= 3.8

## 1.0.3

- dependency updates
  - Adds LXML dependency
  - python >= 3.7
- black-formatted
- adds pre-commit checks (black, flake8)
- adds index template

## 1.0.2

- update dependencies for PyYAML (5 or greater)

## 1.0.1

- update dependencies for newer versions of
  - BeautifulSoup4 4.9.3 to 5
  - ukedown v2-3
  - Markdown v3-4

## 1.0.0

- Initial Release (limited functionality)
- creates Song and SongBook objects from directories and files.
- Generates Index
