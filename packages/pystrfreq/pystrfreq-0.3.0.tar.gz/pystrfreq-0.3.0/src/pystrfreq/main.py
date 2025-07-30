import argparse
import ast
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


def extract_string_from_file(path: Path, is_ignore_docstring: bool) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []

    all_strings: list[str] = []
    doc_strings: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            all_strings.append(node.value)

        if is_ignore_docstring and isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            doc_string: str | None = ast.get_docstring(node)

            if doc_string:
                doc_strings.append(doc_string)

    if is_ignore_docstring:
        for ds in doc_strings:
            all_strings.remove(ds)

    return all_strings


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pystrfreq", description="count strings in Python files"
    )
    parser.add_argument("files_or_dirs", nargs="*", help="files or directories to scan")
    parser.add_argument(
        "--min-count",
        "-m",
        type=int,
        default=1,
        help="show only strings with count equals to or is above this threshold",
    )
    parser.add_argument(
        "--ignore-docstring", "-nd", action="store_true", help="ignore docstrings"
    )

    args = parser.parse_args()

    python_glob_pattern: str = "*.py"
    python_extension: str = ".py"

    counter = Counter()

    if args.files_or_dirs:
        list_of_files: list[Path] = []

        for arg in args.files_or_dirs:
            current_dir_arg = Path(arg)

            if (
                current_dir_arg.is_file()
                and arg.endswith(python_extension)
                and current_dir_arg.exists()
            ):
                list_of_files.append(current_dir_arg)

            elif current_dir_arg.is_dir():
                list_of_files.extend(current_dir_arg.rglob(python_glob_pattern))

            else:
                print(f"{arg}: No such file or directory.")

    else:
        list_of_files: Generator[Path, None, None] = (
            path for path in Path().rglob(python_glob_pattern)
        )

    for path in list_of_files:
        strings: list[str] = extract_string_from_file(path, args.ignore_docstring)
        counter.update(strings)

    largest_freq_len: int = len(str(counter.most_common()[0][1]))

    for s, n in counter.most_common():
        if n >= args.min_count:
            print(f"{str(n).zfill(largest_freq_len)} {s!r}")


if __name__ == "__main__":
    main()
