# lorem\_gen

`lorem_gen` is a lightweight Python package and command-line tool that generates Lorem Ipsum placeholder text. It supports generating a specified number of words, sentences, or paragraphs. This package can be used both as a CLI and as an importable library in other Python projects.

## Features

* Generate a custom number of Lorem Ipsum words, sentences, or paragraphs.
* Simple, dependency-free implementation (built-in Python standard library only).
* CLI interface via the `genrqtor` command.
* Programmatic API through the `LoremGenerator` class.

## Installation

Install `lorem_gen` in editable (development) mode or as a regular package. It requires Python 3.8 or newer.

```bash
# (Optional) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade packaging tools
pip install --upgrade pip setuptools wheel

# Install lorem_gen in editable mode
pip install -e .
```

After installation, the package is importable via `import lorem_gen` and the CLI command `genrqtor` is registered on your PATH.

## Usage

### Command-Line Interface (CLI)

The tool is exposed as `genrqtor`. Run the following for help:

```bash
genrqtor --help
```

Output:

```
usage: genrqtor [-h] [--words WORDS | --sentences SENTENCES | --paragraphs PARAGRAPHS]

Generate Lorem Ipsum text.

optional arguments:
  -h, --help           show this help message and exit
  --words WORDS        Number of words to generate (e.g., --words 50).
  --sentences SENTENCES
                       Number of sentences to generate (e.g., --sentences 5).
  --paragraphs PARAGRAPHS
                       Number of paragraphs to generate (e.g., --paragraphs 2).
```

Examples:

* Generate 50 words of Lorem Ipsum:

  ```bash
  genrqtor --words 50
  ```

* Generate 5 sentences of Lorem Ipsum:

  ```bash
  genrqtor --sentences 5
  ```

* Generate 2 paragraphs of Lorem Ipsum:

  ```bash
  genrqtor --paragraphs 2
  ```

* Default (no flags) generates a single paragraph:

  ```bash
  genrqtor
  ```

### Programmatic API

You can also use `lorem_gen` in your own Python code by importing the `LoremGenerator` class.

```python
from lorem_gen.generator import LoremGenerator

# Generate 20 words:
gen_words = LoremGenerator(words=20)
print(gen_words.generate())

# Generate 3 sentences:
gen_sentences = LoremGenerator(sentences=3)
print(gen_sentences.generate())

# Generate 2 paragraphs:
gen_paragraphs = LoremGenerator(paragraphs=2)
print(gen_paragraphs.generate())
```

#### API Reference

* **`LoremGenerator(words: int = 0, sentences: int = 0, paragraphs: int = 0)`**

  * Constructor. Specify exactly one of `words`, `sentences`, or `paragraphs` to control output. If none provided, defaults to 1 paragraph.

* **`LoremGenerator.generate() -> str`**

  * Returns the generated Lorem Ipsum text as a string.

* **`--words <int>`**

  * CLI flag to generate a certain number of words.

* **`--sentences <int>`**

  * CLI flag to generate a certain number of sentences.

* **`--paragraphs <int>`**

  * CLI flag to generate a certain number of paragraphs.

## Development & Testing

### Running Tests

A basic pytest-based test suite is provided in the `tests/` directory. To run tests:

```bash
pip install pytest         # If not already installed
pytest
```

### Linting & Formatting

You can add `flake8` or other linters to your development dependencies. A sample `requirements-dev.txt` may include:

```
pytest>=7.0
flake8>=5.0
```

Install with:

```bash
pip install -r requirements-dev.txt
```

Then run:

```bash
flake8 src/lorem_gen
tests
```

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/my-new-feature`.
3. Make your changes and commit: `git commit -am 'Add new feature'`.
4. Push to the branch: `git push origin feature/my-new-feature`.
5. Open a Pull Request.

Please follow the existing code style, include tests for new features, and update this README as needed.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
