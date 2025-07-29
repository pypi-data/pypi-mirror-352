import codecs
import json
import os
from datetime import datetime
from pathlib import Path


def make_session_id() -> str:
    return f"{datetime.now():%y%m%d%H%M%S}"


def read_json(path: Path | os.PathLike[str] | str) -> list | dict:
    with codecs.open(path, "r", encoding="utf8") as file:
        return json.load(file)


def try_parse_json(text: str | None) -> str | None:
    if not text:
        return None
    if not text.startswith('{'):
        return None
    if not text.endswith('}'):
        return None
    try:
        return json.loads(text)
    except Exception:
        return None
