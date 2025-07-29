## Usage

```bash
uvx pystrfreq
```

The tool will walk through the current directory, parse all `.py` file and then tabluate the frequency of string in the parsed files.

## Options

```
usage: pystrfreq [-h] [--min-count MIN_COUNT] [files_or_dirs ...]

count strings in Python files

positional arguments:
  files_or_dirs         files or directories to scan

optional arguments:
  -h, --help            show this help message and exit
  --min-count MIN_COUNT, -m MIN_COUNT
                        show only strings with count equals to or is above this threshold
```

## Known Caveats

- This package does not support parsing python version < 3.9
- `FormmatedValue` in `f-string` are not supported, while the `f-string` will be broken into its constant parts and tabulated.

## License

This project is licensed under the MIT License.
