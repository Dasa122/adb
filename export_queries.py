#!/usr/bin/env python3
"""
export_queries.py

Runs every statement in a .sql file against MySQL/MariaDB and saves the result
of each statement into its own file (CSV / TSV / JSON / Markdown).

Features
--------
* Works with any .sql file - statements are split correctly, respecting
  strings, backticks and --, #, /* */ comments.
* All statements run in ONE session, so USE, SET @vars and temp tables keep
  working across statements.
* Writes a _log.txt summarising every statement, plus _stderr.log on errors.
* Supports a server running inside a Docker container (the password is read
  from the container's own environment, so it never touches the command line
  or this file).

Examples
--------
# database taken from the file's own USE statement
python3 export_queries.py 3/lekerdezesek.sql

# MySQL in a Docker container
python3 export_queries.py 3/lekerdezesek.sql --container mysql -u root

# plain local server (password via the MYSQL_PWD env var)
python3 export_queries.py queries.sql -H 127.0.0.1 -P 3306 -u root -d shop

# Markdown tables instead of CSV
python3 export_queries.py queries.sql -f md -o out/
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field

MARKER = "@@EXPORT_MARKER:{}@@"
QUOTES = "'\"`"
ESCAPES = {
    "0": "\0",
    "b": "\b",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "Z": "\x1a",
    "\\": "\\",
    "'": "'",
    '"': '"',
}


# --------------------------------------------------------------------------- #
# SQL parsing
# --------------------------------------------------------------------------- #
@dataclass
class Statement:
    index: int
    sql: str
    label: str = ""
    start_line: int = 0
    end_line: int = 0
    header: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    error: str = ""

    @property
    def has_result(self) -> bool:
        return bool(self.header)


def split_statements(text: str) -> list[Statement]:
    """Split a script into statements, ignoring ; inside strings and comments."""
    statements: list[Statement] = []
    buf: list[str] = []
    comments: list[str] = []
    i, n = 0, len(text)

    def flush() -> None:
        sql = "".join(buf).strip()
        if sql:
            label = next((c for c in comments if c), "")
            statements.append(Statement(len(statements) + 1, sql, label))
        buf.clear()
        comments.clear()

    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if ch == "-" and nxt == "-" and (i + 2 >= n or text[i + 2] in " \t\r\n"):
            end = text.find("\n", i)
            end = n if end == -1 else end
            comments.append(text[i:end].lstrip("-").strip())
            i = end
            continue

        if ch == "#":
            end = text.find("\n", i)
            end = n if end == -1 else end
            comments.append(text[i:end].lstrip("#").strip())
            i = end
            continue

        if ch == "/" and nxt == "*":
            end = text.find("*/", i + 2)
            end = n if end == -1 else end + 2
            comments.append(text[i + 2 : max(i + 2, end - 2)].strip())
            i = end
            continue

        if ch in QUOTES:
            quote = ch
            buf.append(ch)
            i += 1
            while i < n:
                c = text[i]
                buf.append(c)
                if c == "\\" and quote != "`":
                    i += 1
                    if i < n:
                        buf.append(text[i])
                        i += 1
                    continue
                if c == quote:
                    if i + 1 < n and text[i + 1] == quote:
                        buf.append(text[i + 1])
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue

        if ch == ";":
            flush()
            i += 1
            continue

        buf.append(ch)
        i += 1

    flush()
    return statements


def unescape(value: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(value):
        if value[i] == "\\" and i + 1 < len(value):
            nxt = value[i + 1]
            out.append(ESCAPES.get(nxt, nxt))
            i += 2
            continue
        out.append(value[i])
        i += 1
    return "".join(out)


# --------------------------------------------------------------------------- #
# Naming
# --------------------------------------------------------------------------- #
def slug(text: str, limit: int = 50) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    )
    ascii_text = re.sub(r"[^A-Za-z0-9]+", "_", ascii_text).strip("_").lower()
    return ascii_text[:limit].strip("_") or "result"


def auto_name(sql: str) -> str:
    flat = re.sub(r"\s+", " ", sql).strip().lstrip("( \t")
    # drop column aliases so they don't appear twice in the file name
    flat = re.sub(r"\bas\s+[`\"]?\w+[`\"]?", " ", flat, flags=re.IGNORECASE)
    flat = re.sub(r"\s+", " ", flat).strip()
    verb = re.split(r"[\s(]+", flat, maxsplit=1)[0].lower() or "query"
    match = re.search(r"\bfrom\s+([`\"\w.]+)", flat, re.IGNORECASE)
    if match:
        table = match.group(1).strip("`\"").replace(".", "_")
        return slug(f"{verb}_{table}")
    return slug("_".join(flat.split()[:4]))


# --------------------------------------------------------------------------- #
# Running
# --------------------------------------------------------------------------- #
def build_command(args: argparse.Namespace) -> list[str]:
    if args.container:
        inner = [
            f'MYSQL_PWD="${{{args.password_env}}}"',
            "mysql",
            "-u",
            shlex.quote(args.user),
            "--batch",
            "--force",
            "--default-character-set=utf8mb4",
        ]
        if args.database:
            inner += ["-D", shlex.quote(args.database)]
        return ["docker", "exec", "-i", args.container, "sh", "-c", " ".join(inner)]

    exe = shutil.which("mysql") or shutil.which("mariadb") or "mysql"
    cmd = [
        exe,
        "-u",
        args.user,
        "--batch",
        "--force",
        "--default-character-set=utf8mb4",
    ]
    if args.host:
        cmd += ["--host", args.host]
    if args.port:
        cmd += ["--port", str(args.port)]
    if args.database:
        cmd += ["--database", args.database]
    return cmd


def execute(args: argparse.Namespace, statements: list[Statement]) -> tuple[str, str]:
    """Run all statements in a single session, returning (stdout, stderr)."""
    lines: list[str] = []
    for st in statements:
        st.start_line = len(lines) + 1
        lines.append(f"SELECT '{MARKER.format(st.index)}' AS m;")
        for chunk in st.sql.splitlines() or [""]:
            lines.append(chunk)
        lines[-1] = lines[-1].rstrip() + ";"
        st.end_line = len(lines)
        lines.append("")

    script = "\n".join(lines)
    env = dict(os.environ)
    if not args.container and args.password:
        env["MYSQL_PWD"] = args.password

    proc = subprocess.run(
        build_command(args),
        input=script,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return proc.stdout, proc.stderr


def parse_output(statements: list[Statement], stdout: str) -> None:
    lookup = {st.index: st for st in statements}
    lines = [line.rstrip("\r") for line in stdout.split("\n")]
    current: Statement | None = None

    for pos, line in enumerate(lines):
        match = re.fullmatch(r"@@EXPORT_MARKER:(\d+)@@", line.strip())
        if match:
            # The line right before a marker is that marker's own column header
            # ("m"), so drop it from whatever the previous statement collected.
            if current is not None and pos > 0 and lines[pos - 1] == "m":
                if not current.rows and current.header == ["m"]:
                    current.header = []
                elif current.rows and current.rows[-1] == ["m"]:
                    current.rows.pop()
            current = lookup.get(int(match.group(1)))
            current.rows = []
            continue

        if current is None:
            continue

        fields = [unescape(f) for f in line.split("\t")]
        if not current.header:
            if line == "":
                continue
            current.header = fields
        else:
            current.rows.append(fields)

    for st in statements:
        while st.rows and st.rows[-1] == [""]:
            st.rows.pop()


def attribute_errors(statements: list[Statement], stderr: str) -> None:
    for line in stderr.splitlines():
        match = re.search(r"\bat line (\d+)\b", line)
        if not match:
            continue
        lineno = int(match.group(1))
        for st in statements:
            if st.start_line <= lineno <= st.end_line:
                st.error = re.sub(r"^ERROR \d+ \([^)]*\) at line \d+: ?", "", line)
                break


# --------------------------------------------------------------------------- #
# Writing
# --------------------------------------------------------------------------- #
def write_csv(path: str, header: list[str], rows: list[list[str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)


def write_tsv(path: str, header: list[str], rows: list[list[str]]) -> None:
    def clean(value: str) -> str:
        return value.replace("\t", " ").replace("\n", " ").replace("\r", " ")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\t".join(clean(h) for h in header) + "\n")
        for row in rows:
            fh.write("\t".join(clean(c) for c in row) + "\n")


def write_json(path: str, header: list[str], rows: list[list[str]]) -> None:
    data = [dict(zip(header, row)) for row in rows]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def write_md(path: str, header: list[str], rows: list[list[str]]) -> None:
    def clean(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", "<br>")

    widths = [max(len(clean(header[i])), *(len(clean(r[i])) for r in rows)) if rows
              else len(clean(header[i])) for i in range(len(header))]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("| " + " | ".join(clean(h).ljust(widths[i])
                                   for i, h in enumerate(header)) + " |\n")
        fh.write("|" + "|".join("-" * (w + 2) for w in widths) + "|\n")
        for row in rows:
            fh.write("| " + " | ".join(clean(c).ljust(widths[i])
                                       for i, c in enumerate(row)) + " |\n")


WRITERS = {"csv": write_csv, "tsv": write_tsv, "json": write_json, "md": write_md}


def write_results(args: argparse.Namespace, statements: list[Statement]) -> None:
    os.makedirs(args.outdir, exist_ok=True)
    writer = WRITERS[args.format]
    log: list[str] = []

    for st in statements:
        if not st.has_result:
            status = f"ERROR  {st.error}" if st.error else "no result set"
            log.append(f"{st.index:02d}  {status}  (nothing written)")
            continue

        name = slug(st.label) if st.label else auto_name(st.sql)
        filename = f"{st.index:02d}_{name}.{args.format}"
        writer(os.path.join(args.outdir, filename), st.header, st.rows)
        log.append(f"{st.index:02d}  ok  {len(st.rows)} row(s)  -> {filename}")

    header = f"source: {args.sqlfile}   format: {args.format}\n"
    with open(os.path.join(args.outdir, "_log.txt"), "w", encoding="utf-8") as fh:
        fh.write(header + "\n".join(log) + "\n")

    print(header + "\n".join(log))


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run every statement in a .sql file and write each result "
                    "set to its own file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("sqlfile", help="the .sql file to process")
    parser.add_argument("-o", "--outdir",
                        help="output directory (default: <name>_results next to "
                             "the .sql file)")
    parser.add_argument("-f", "--format", choices=sorted(WRITERS), default="csv",
                        help="output format (default: csv)")
    parser.add_argument("-d", "--database", help="initial database to use")
    parser.add_argument("-c", "--container",
                        help="run mysql inside this Docker container")
    parser.add_argument("-e", "--password-env", default="MYSQL_ROOT_PASSWORD",
                        help="container env var holding the password "
                             "(default: MYSQL_ROOT_PASSWORD)")
    parser.add_argument("-H", "--host", help="database host (local server mode)")
    parser.add_argument("-P", "--port", type=int, help="database port")
    parser.add_argument("-u", "--user", default="root", help="database user")
    parser.add_argument("-p", "--password",
                        help="password (local mode; prefer the MYSQL_PWD env var)")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.sqlfile):
        parser.error(f"file not found: {args.sqlfile}")

    if not args.outdir:
        stem = os.path.splitext(os.path.basename(args.sqlfile))[0]
        args.outdir = os.path.join(os.path.dirname(args.sqlfile) or ".",
                                   f"{stem}_results")

    with open(args.sqlfile, encoding="utf-8") as fh:
        text = fh.read()

    statements = split_statements(text)
    if not statements:
        print("no statements found", file=sys.stderr)
        return 1

    stdout, stderr = execute(args, statements)
    parse_output(statements, stdout)
    attribute_errors(statements, stderr)

    write_results(args, statements)

    if stderr.strip():
        noise = re.compile(r"^mysql: \[Warning\] Using a password")
        messages = "\n".join(l for l in stderr.splitlines() if not noise.match(l))
        if messages.strip():
            log_path = os.path.join(args.outdir, "_stderr.log")
            with open(log_path, "w", encoding="utf-8") as fh:
                fh.write(messages + "\n")
            print(f"\n-- database messages --\n{messages}", file=sys.stderr)
            print(f"\n(full messages written to {log_path})", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
