## Usage

```bash
uvx pystrfreq
```

The script will walk through the current directory, parse all `.py` file and then tabluate the frequency of string in the parsed files.

## Known Caveats

- This package does not support parsing python version < 3.9
- `FormmatedValue` in `f-string` are not supported, while the `f-string` will be broken into its constant parts and tabulated.

## License

This project is licensed under the MIT License.
