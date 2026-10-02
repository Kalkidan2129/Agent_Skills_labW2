"""Check Skills for the common mistakes that stop them from triggering.

Usage:
    python tools/check_skills.py                 (checks .claude/skills in this folder)
    python tools/check_skills.py <skills-folder> (e.g. ~/.claude/skills)

Uses the standard library; uses PyYAML for a stricter check if it's installed.
"""

import os
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TRIGGER_WORDS = ("use this", "use when", "whenever", "use for", "when the user", "if the user")
VAGUE_PHRASES = ("helps with", "a useful skill", "various tasks", "does stuff", "general purpose",
                 "assists with things")


def parse_frontmatter(text):
    """Return (fields, error). fields is a dict of the frontmatter."""
    if text.startswith("﻿"):
        text = text[1:]
    if not text.startswith("---"):
        return None, "File doesn't start with '---', so the label block is missing or has text above it."
    match = re.match(r"^---\r?\n(.*?)\r?\n---\s*(\r?\n|$)", text, re.S)
    if not match:
        return None, "Opening '---' found but no closing '---' line."
    block = match.group(1)
    if "\t" in block:
        return None, "Label block contains a Tab character; YAML only allows spaces for indentation."
    if yaml:
        try:
            data = yaml.safe_load(block) or {}
        except yaml.YAMLError as e:
            first_line = str(e).splitlines()[0]
            return None, f"Label block isn't valid YAML ({first_line}). A common cause is an unquoted ': ' inside the description."
        if not isinstance(data, dict):
            return None, "Label block isn't a list of 'key: value' lines."
        return data, None
    # Fallback without PyYAML: simple top-level key: value lines only.
    data = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            data[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return data, None


def check_skill(folder):
    problems, warnings = [], []
    folder_name = os.path.basename(folder)
    files = os.listdir(folder)
    skill_md = os.path.join(folder, "SKILL.md")

    if "SKILL.md" not in files:
        near = [f for f in files if f.lower() in ("skill.md", "skill.txt", "skill.md.txt", "readme.md")]
        hint = f" Found '{near[0]}' instead; rename it to exactly 'SKILL.md'." if near else ""
        problems.append(f"No SKILL.md file in this folder.{hint}")
        return problems, warnings

    with open(skill_md, encoding="utf-8", errors="replace") as f:
        text = f.read()
    data, error = parse_frontmatter(text)
    if error:
        problems.append(error)
        return problems, warnings

    name = str(data.get("name") or folder_name)
    if not NAME_RE.match(name):
        problems.append(f"Name '{name}' must be lowercase letters, numbers and hyphens only (no spaces or capitals).")
    if data.get("name") and data["name"] != folder_name:
        warnings.append(f"Name '{data['name']}' differs from the folder name '{folder_name}'. Keep them the same to avoid confusion.")

    desc = str(data.get("description") or "").strip()
    if not desc:
        problems.append("No description. Claude decides when to use a Skill from its description, so without one it can't trigger.")
    else:
        if len(desc) > 1024:
            problems.append(f"Description is {len(desc)} characters; the limit is 1024.")
        if len(desc) < 80:
            warnings.append(f"Description is only {len(desc)} characters. Add when to use it and the words people actually say.")
        if not any(w in desc.lower() for w in TRIGGER_WORDS):
            warnings.append("Description says what the Skill does but not WHEN to use it. Add a 'Use this whenever...' sentence.")
        vague = [p for p in VAGUE_PHRASES if p in desc.lower()]
        if vague:
            warnings.append(f"Description uses vague wording ({', '.join(vague)}). Name the specific task instead.")

    if str(data.get("disable-model-invocation")).lower() == "true":
        problems.append("disable-model-invocation is true, so Claude will NEVER start this Skill on its own; only typing the /command works. Remove that line if you want automatic use.")
    if data.get("paths"):
        warnings.append(f"paths is set ({data['paths']}), so the Skill only starts automatically when working with matching files.")

    body = text.split("---", 2)[-1]
    if re.search(r"(?im)^\s*(use (this|it) (when|whenever)|when to use)", body):
        warnings.append("The body contains 'when to use' guidance. Claude reads the body only AFTER choosing the Skill, so move it into the description.")
    return problems, warnings


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(".claude", "skills")
    root = os.path.expanduser(root)
    if not os.path.isdir(root):
        sys.exit(f"Folder not found: {root}\nSkills must live in .claude/skills/<skill-name>/ or ~/.claude/skills/<skill-name>/")

    print(f"Checking Skills in: {os.path.abspath(root)}\n")
    stray = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
    for f in stray:
        print(f"[PROBLEM] '{f}' sits directly in the skills folder. Each Skill needs its own folder: {root}/<skill-name>/SKILL.md\n")

    total_problems = len(stray)
    for entry in sorted(os.listdir(root)):
        folder = os.path.join(root, entry)
        if not os.path.isdir(folder):
            continue
        problems, warnings = check_skill(folder)
        total_problems += len(problems)
        status = "PROBLEMS" if problems else ("CHECK" if warnings else "OK")
        print(f"== {entry}: {status}")
        for p in problems:
            print(f"   [PROBLEM] {p}")
        for w in warnings:
            print(f"   [CHECK]   {w}")
        print()
    if yaml is None:
        print("(PyYAML not installed, so the YAML check was basic. Install it with: pip install pyyaml)")
    print("Done. Fix every [PROBLEM] first; [CHECK] items are about how often the Skill triggers.")


if __name__ == "__main__":
    main()
