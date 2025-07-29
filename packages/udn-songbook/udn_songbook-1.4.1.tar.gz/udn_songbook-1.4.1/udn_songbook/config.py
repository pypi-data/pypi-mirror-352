from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="UDN_SONGBOOK",
    settings_files=[
        Path("~/.config/udn-songbook/settings.toml").expanduser(),
        Path(__file__).parent / "defaults.toml",
    ],
    environments=False,
    merge_enabled=True,
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
