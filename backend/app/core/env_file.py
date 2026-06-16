from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Mapping


ENV_FILE_PATH_KEY = 'ENV_FILE_PATH'


def env_file_path() -> Path:
    return Path(os.environ.get(ENV_FILE_PATH_KEY, '.env')).resolve()


def update_env_file(values: Mapping[str, object], path: Path | None = None) -> Path:
    target = (path or env_file_path()).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    existing = target.read_text(encoding='utf-8') if target.exists() else ''
    lines = existing.splitlines(keepends=True)
    pending = {key: _format_env_line(key, value) for key, value in values.items()}
    key_pattern = re.compile(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=')
    updated_lines: list[str] = []

    for line in lines:
        match = key_pattern.match(line)
        if match and match.group(1) in pending:
            updated_lines.append(pending.pop(match.group(1)))
        else:
            updated_lines.append(line)

    if pending:
        if updated_lines and not updated_lines[-1].endswith(('\n', '\r')):
            updated_lines[-1] = f'{updated_lines[-1]}\n'
        if updated_lines and updated_lines[-1].strip():
            updated_lines.append('\n')
        updated_lines.extend(pending.values())

    target.write_text(''.join(updated_lines), encoding='utf-8')
    for key, value in values.items():
        os.environ[key] = _env_value(value)
    return target


def _format_env_line(key: str, value: object) -> str:
    return f'{key}={_quote_env_value(_env_value(value))}\n'


def _env_value(value: object) -> str:
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def _quote_env_value(value: str) -> str:
    if value == '':
        return ''
    if re.fullmatch(r'[A-Za-z0-9_./:@,+-]+', value):
        return value
    escaped = (
        value
        .replace('\\', '\\\\')
        .replace('"', '\\"')
        .replace('\r', '')
        .replace('\n', '\\n')
    )
    return f'"{escaped}"'
