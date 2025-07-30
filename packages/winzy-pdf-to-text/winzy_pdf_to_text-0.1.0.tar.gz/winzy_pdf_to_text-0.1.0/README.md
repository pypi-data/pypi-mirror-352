# winzy-pdf-to-text

[![PyPI](https://img.shields.io/pypi/v/winzy-pdf-to-text.svg)](https://pypi.org/project/winzy-pdf-to-text/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/winzy-pdf-to-text?include_prereleases&label=changelog)](https://github.com/sukhbinder/winzy-pdf-to-text/releases)
[![Tests](https://github.com/sukhbinder/winzy-pdf-to-text/workflows/Test/badge.svg)](https://github.com/sukhbinder/winzy-pdf-to-text/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/winzy-pdf-to-text/blob/main/LICENSE)

Extract text from a given pdf

## Installation

First configure your Winzy project [to use Winzy](https://github.com/sukhbinder/winzy).

Then install this plugin in the same environment as your Winzy application.
```bash
pip install winzy-pdf-to-text
```
## Usage

```bash
winzy pdf2text example.pdf -p 1
```

This will extract all text from page 1 to the standard output.

One can also provide range

```bash
winzy pdf2text example.pdf -p 3-6
```
This will extract text from page 3 to 5 .


## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd winzy-pdf-to-text
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
