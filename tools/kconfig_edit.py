#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small, careful editor for KDE/Krita config files (kritarc, kritashortcutsrc).

Changes only the keys it is asked to change and leaves every other line as
it is. Used by install.sh and uninstall.sh.

    kconfig_edit.py FILE get   GROUP KEY
    kconfig_edit.py FILE set   GROUP KEY VALUE
    kconfig_edit.py FILE unset GROUP KEY

GROUP "" means the top-level group (keys before the first [header]).
"""

import os
import sys


def _read(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return fh.read().splitlines()


def _write(path, lines):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".krita2csp-tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip("\n") + "\n")
    os.replace(tmp, path)


def _is_header(line):
    s = line.strip()
    return s.startswith("[") and s.endswith("]") and not s.startswith("[$")


def _group_bounds(lines, group):
    """Return (start, end) line indexes of the group's key lines, or None."""
    if group == "":
        end = next((i for i, l in enumerate(lines) if _is_header(l)), len(lines))
        return 0, end
    header = "[%s]" % group
    for i, line in enumerate(lines):
        if line.strip() == header:
            end = next((j for j in range(i + 1, len(lines)) if _is_header(lines[j])), len(lines))
            return i + 1, end
    return None


def _key_of(line):
    if "=" not in line or line.lstrip().startswith("#"):
        return None
    key = line.split("=", 1)[0].strip()
    # "Key[$e]" or "Key[de]" variants count as the same key name for us
    if key.endswith("]") and "[" in key:
        key = key[:key.index("[")]
    return key


def get(lines, group, key):
    bounds = _group_bounds(lines, group)
    if not bounds:
        return None
    for i in range(*bounds):
        if _key_of(lines[i]) == key:
            return lines[i].split("=", 1)[1]
    return None


def set_value(lines, group, key, value):
    bounds = _group_bounds(lines, group)
    entry = "%s=%s" % (key, value)
    if bounds is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines += ["[%s]" % group, entry]
        return lines
    start, end = bounds
    for i in range(start, end):
        if _key_of(lines[i]) == key:
            lines[i] = entry
            return lines
    insert = end
    while insert > start and not lines[insert - 1].strip():
        insert -= 1
    lines.insert(insert, entry)
    return lines


def unset(lines, group, key):
    bounds = _group_bounds(lines, group)
    if bounds is None:
        return lines
    start, end = bounds
    return [l for i, l in enumerate(lines) if not (start <= i < end and _key_of(l) == key)]


def main(argv):
    if len(argv) < 5:
        print(__doc__)
        return 2
    path, cmd, group, key = argv[1:5]
    lines = _read(path)
    if cmd == "get":
        value = get(lines, group, key)
        if value is None:
            return 1
        print(value)
        return 0
    if cmd == "set" and len(argv) == 6:
        _write(path, set_value(lines, group, key, argv[5]))
        return 0
    if cmd == "unset":
        if lines:
            _write(path, unset(lines, group, key))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
