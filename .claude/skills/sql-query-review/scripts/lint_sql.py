"""Static checks for common SQL mistakes.

Usage:
    python lint_sql.py <file.sql> [more.sql ...]
    python lint_sql.py -        (read SQL from standard input)

Uses only the Python standard library. The checks are pattern-based, so they
flag *likely* problems; the Skill tells Claude to confirm each one by reading
the query before reporting it.
"""

import re
import sys

FLAGS = re.IGNORECASE

# (rule id, severity, pattern, explanation)
RULES = [
    ("null-comparison", "HIGH", r"(?<![<>!])(=|<>|!=)\s*NULL\b",
     "Comparing with = or <> NULL is never true. Use IS NULL / IS NOT NULL."),
    ("not-in-subquery", "HIGH", r"\bNOT\s+IN\s*\(\s*SELECT\b",
     "NOT IN (subquery) returns no rows if the subquery yields any NULL. Prefer NOT EXISTS."),
    ("implicit-join", "MEDIUM", r"\bFROM\s+[\w.\[\]\"`]+(?:\s+(?:AS\s+)?\w+)?\s*,\s*[\w\[\"`]",
     "Comma-style join; a missing condition silently becomes a cross join. Use explicit JOIN ... ON."),
    ("function-on-column", "MEDIUM",
     r"\b(?:WHERE|AND|OR)\s+(?:YEAR|MONTH|DAY|DATE|UPPER|LOWER|TRIM|CAST|CONVERT|SUBSTRING|SUBSTR"
     r"|COALESCE|ISNULL|IFNULL|DATE_TRUNC|EXTRACT|DATEPART|FORMAT)\s*\(",
     "Function wrapped around a column in a filter usually prevents index use. Rewrite as a range."),
    ("select-star", "LOW", r"\bSELECT\s+(?:DISTINCT\s+)?(?:TOP\s+\d+\s+)?\*",
     "SELECT * fetches every column. List only the columns you need."),
    ("select-distinct", "LOW", r"\bSELECT\s+DISTINCT\b",
     "DISTINCT can hide duplicate rows caused by a join. Check whether the join is the real problem."),
    ("union-without-all", "LOW", r"\bUNION\b(?!\s+ALL\b)",
     "UNION removes duplicates (extra sort). Use UNION ALL if duplicates are impossible or fine."),
    ("ordinal-reference", "LOW", r"\b(?:GROUP|ORDER)\s+BY\s+\d",
     "Positional GROUP BY / ORDER BY breaks silently if columns are reordered. Use names."),
]

CLAUSE_END = r"\b(?:GROUP\s+BY|ORDER\s+BY|HAVING|LIMIT|UNION|WINDOW|FETCH|OFFSET)\b"
SQL_KEYWORDS = {"on", "where", "join", "left", "right", "inner", "outer", "full", "cross", "using"}
SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def mask(sql):
    """Blank out comments and string-literal contents (keeping quotes, length and
    newlines) so patterns never match inside them and line numbers stay right."""
    out = list(sql)
    n = len(sql)

    def blank(start, end):
        for k in range(start, min(end, n)):
            if out[k] != "\n":
                out[k] = " "

    i = 0
    while i < n:
        if sql.startswith("--", i):
            end = sql.find("\n", i)
            end = n if end == -1 else end
            blank(i, end)
            i = end
        elif sql.startswith("/*", i):
            end = sql.find("*/", i + 2)
            end = n if end == -1 else end + 2
            blank(i, end)
            i = end
        elif sql[i] == "'":
            j = i + 1
            while j < n:
                if sql[j] == "'" and j + 1 < n and sql[j + 1] == "'":
                    j += 2  # escaped quote ''
                    continue
                if sql[j] == "'":
                    break
                j += 1
            blank(i + 1, j)
            i = j + 1
        else:
            i += 1
    return "".join(out)


def lint(sql):
    masked = mask(sql)
    lines = sql.splitlines()
    findings = []

    def add(rule, severity, pos, why):
        line_no = masked.count("\n", 0, pos) + 1
        snippet = lines[line_no - 1].strip() if line_no <= len(lines) else ""
        findings.append((line_no, severity, rule, snippet, why))

    for rule, severity, pattern, why in RULES:
        for m in re.finditer(pattern, masked, FLAGS):
            add(rule, severity, m.start(), why)

    # Leading wildcard: the masked text keeps the quote, the original keeps the content.
    for m in re.finditer(r"\bLIKE\s+'", masked, FLAGS):
        if sql[m.end():m.end() + 1] == "%":
            add("leading-wildcard", "MEDIUM", m.start(),
                "LIKE '%...' (leading wildcard) can't use an index and scans every row.")

    # Per-statement checks.
    offset = 0
    statements = 0
    for stmt in masked.split(";"):
        if stmt.strip():
            statements += 1
            head = re.match(r"\s*(UPDATE|DELETE)\b", stmt, FLAGS)
            if head and not re.search(r"\bWHERE\b", stmt, FLAGS):
                verb = head.group(1).upper()
                add(f"{verb.lower()}-without-where", "HIGH", offset + head.start(1),
                    f"{verb} with no WHERE clause affects every row in the table.")

            # LEFT JOIN undone by a WHERE filter on the right-hand table.
            aliases = []
            for j in re.finditer(r"\bLEFT\s+(?:OUTER\s+)?JOIN\s+([\w.]+)(?:\s+(?:AS\s+)?(\w+))?", stmt, FLAGS):
                table, alias = j.group(1), j.group(2)
                if alias and alias.lower() in SQL_KEYWORDS:
                    alias = None
                aliases.append(alias or table.split(".")[-1])
            where = re.search(r"\bWHERE\b", stmt, FLAGS)
            if aliases and where:
                clause = stmt[where.end():]
                end = re.search(CLAUSE_END, clause, FLAGS)
                clause = clause[:end.start()] if end else clause
                for alias in aliases:
                    for c in re.finditer(rf"\b{re.escape(alias)}\.\w+\s*(?!IS\b)(=|<>|!=|<=|>=|<|>|IN\b|LIKE\b|BETWEEN\b)",
                                         clause, FLAGS):
                        add("left-join-filtered", "HIGH", offset + where.end() + c.start(),
                            f"WHERE filters on '{alias}', the right side of a LEFT JOIN; unmatched rows are "
                            "dropped, so it behaves like an INNER JOIN. Move the condition into ON.")
        offset += len(stmt) + 1

    findings.sort(key=lambda f: (SEVERITY_ORDER[f[1]], f[0]))
    return statements, findings


def report(name, sql):
    statements, findings = lint(sql)
    counts = {s: sum(1 for f in findings if f[1] == s) for s in SEVERITY_ORDER}
    print(f"# SQL lint: {name}")
    print(f"Statements: {statements} | Findings: {len(findings)} "
          f"(HIGH {counts['HIGH']}, MEDIUM {counts['MEDIUM']}, LOW {counts['LOW']})")
    if not findings:
        print("No pattern-level issues found. Still review logic with the checklist.")
    for line_no, severity, rule, snippet, why in findings:
        print(f"\n[{severity}] line {line_no}  {rule}")
        print(f"  Code: {snippet}")
        print(f"  Why:  {why}")
    print()


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit("Usage: python lint_sql.py <file.sql> [...]  |  python lint_sql.py -")
    for path in args:
        if path == "-":
            report("(stdin)", sys.stdin.read())
        else:
            with open(path, encoding="utf-8-sig") as f:
                report(path, f.read())


if __name__ == "__main__":
    main()
