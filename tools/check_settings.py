"""Refuse to commit settings.py unless its deployment values are blank.

detect-secrets catches the SECRET_KEY, but not a database password written as
'PASS' or an address in EMAIL_HOST_USER, so those are checked by name here.
Real values belong only in the copy on the server.
"""
import re
import sys
from pathlib import Path

SETTINGS = Path("pgcontrib/settings.py")
ALWAYS_BLANK = ("SECRET_KEY", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "DEFAULT_FROM_EMAIL")
DATABASE_BLANK = ("NAME", "USER", "PASS", "PASSWORD", "HOST")


def filled(line, key):
    return re.match(rf"\s*'?{key}'?\s*[:=]\s*['\"].+['\"]", line)


def main():
    if not SETTINGS.exists():
        return 0

    problems = []
    in_databases = False
    for number, line in enumerate(SETTINGS.read_text().splitlines(), start=1):
        if re.match(r"\s*DATABASES\s*=", line):
            in_databases = True
        elif in_databases and line.startswith("}"):
            in_databases = False

        keys = ALWAYS_BLANK + (DATABASE_BLANK if in_databases else ())
        for key in keys:
            if filled(line, key):
                problems.append(f"  {SETTINGS}:{number} {key} is not blank")
        if re.match(r"\s*DEBUG\s*=\s*True", line):
            problems.append(f"  {SETTINGS}:{number} DEBUG is on")

    if problems:
        print("Deployment values must not be committed:", *problems, sep="\n")
        print("\nBlank them in the staged copy. The real values stay on the server.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
