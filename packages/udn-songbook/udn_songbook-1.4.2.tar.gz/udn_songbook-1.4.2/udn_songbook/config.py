from pathlib import Path

import dynaconf  # type: ignore[import-untyped]
from platformdirs import PlatformDirs

# use system-specific paths for default configs
DEFAULT_SETTINGS_FILES = [
    PlatformDirs("udn_songbook").user_config_path / "settings.toml",
    Path(__file__).parent / "defaults.toml",
]


# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
#
def load_settings(settings_files: list[Path] = []) -> dynaconf.LazySettings:
    """Load settings from the provided list of files.

    Args:
        settings_files(list[Path]): list of pathlib.Path objects to look for.

    """
    # preprend custom config paths to settings_files

    settings_files.extend(DEFAULT_SETTINGS_FILES)

    return dynaconf.Dynaconf(
        envvar_prefix="UDN_SONGBOOK",
        settings_files=settings_files,
        environments=False,
        merge_enabled=True,
        load_dotenv=True,
    )
