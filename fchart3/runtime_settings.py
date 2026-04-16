import argparse
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional


CONFIG_TO_ARG_ATTR = {
    "extra_data_dir": "extra_data_dir",
    "width": "width",
    "height": "height",
    "landscape_paper": "landscape_paper",
    "force_messier": "force_messier",
    "force_asterisms": "force_asterisms",
    "force_unknown": "force_unknown",
    "language": "language",
    "show_catalogs": "show_catalogs",
    "caption": "caption",
    "mirror_x": "mirror_x",
    "mirror_y": "mirror_y",
    "observation_time": "dt",
    "trajectory_from": "trajectory_from",
    "trajectory_to": "trajectory_to",
    "mpc_comets_file": "mpc_comets_file",
    "mpc_minor_planets_file": "mpc_minor_planets_file",
}

FLOAT_KEYS = {
    "width",
    "height",
}

BOOLEAN_KEYS = {
    "landscape_paper",
    "force_messier",
    "force_asterisms",
    "force_unknown",
    "mirror_x",
    "mirror_y",
}

OPTIONAL_STRING_KEYS = {
    "extra_data_dir",
    "show_catalogs",
    "caption",
}

STRING_KEYS = {
    "language",
    "mpc_comets_file",
    "mpc_minor_planets_file",
}

DATETIME_KEYS = {
    "observation_time",
    "trajectory_from",
    "trajectory_to",
}


def parse_bool(value_str):
    v = value_str.strip().lower()
    return v in ("true", "1", "yes", "y", "on")


def parse_optional_string(value_str):
    v = value_str.strip()
    if v.lower() in ("", "none", "null"):
        return None
    return v


def parse_observation_time(value: str) -> datetime:
    s = value.strip()
    if s.lower() in ("now",):
        return datetime.now(timezone.utc)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid observation_time value '{value}'. Expected ISO-8601, e.g. "
            f"2026-01-02T21:15:00Z or 2026-01-02T21:15:00+01:00, or 'now'."
        ) from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_time_or_date(value: str) -> datetime:
    s = value.strip()
    if not s:
        raise argparse.ArgumentTypeError("Empty datetime/date value")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        pass

    try:
        d = date.fromisoformat(s)
        return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid value '{value}'. Expected ISO-8601 datetime or date."
        ) from e


@dataclass(slots=True)
class RuntimeConfiguration:
    extra_data_dir: Optional[str] = None
    width: float = 180.0
    height: float = 270.0
    landscape_paper: bool = False
    force_messier: bool = False
    force_asterisms: bool = False
    force_unknown: bool = False
    language: str = "en"
    show_catalogs: Optional[str] = None
    caption: Optional[str] = None
    mirror_x: bool = False
    mirror_y: bool = False
    observation_time: Optional[datetime] = None
    trajectory_from: Optional[datetime] = None
    trajectory_to: Optional[datetime] = None
    mpc_comets_file: Optional[str] = "CometEls.txt"
    mpc_minor_planets_file: Optional[str] = "MPCORB.9999.DAT"
    cross: list[str] = field(default_factory=list)


class RuntimeConfigurationLoader:
    def __init__(self, config_file):
        self.config_file = config_file

    def load_config(self, config: RuntimeConfiguration):
        with open(self.config_file, "r") as f:
            lines = f.readlines()

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            try:
                if key == "cross":
                    config.cross.append(value)
                elif key in FLOAT_KEYS and hasattr(config, key):
                    setattr(config, key, float(value))
                elif key in BOOLEAN_KEYS and hasattr(config, key):
                    setattr(config, key, parse_bool(value))
                elif key in OPTIONAL_STRING_KEYS and hasattr(config, key):
                    setattr(config, key, parse_optional_string(value))
                elif key in STRING_KEYS and hasattr(config, key):
                    setattr(config, key, value)
                elif key in DATETIME_KEYS and hasattr(config, key):
                    if key == "observation_time":
                        setattr(config, key, parse_observation_time(value))
                    else:
                        setattr(config, key, parse_time_or_date(value))
            except Exception:
                continue

        return True


def apply_runtime_config_defaults(args, runtime_config: RuntimeConfiguration):
    for config_attr, arg_attr in CONFIG_TO_ARG_ATTR.items():
        if getattr(args, arg_attr, None) is None:
            setattr(args, arg_attr, getattr(runtime_config, config_attr))

    if not getattr(args, "cross_marks", None):
        args.cross_marks = list(runtime_config.cross)
    else:
        args.cross_marks = list(runtime_config.cross) + list(args.cross_marks)

    return args
