![fontsplitta-logo](https://github.com/user-attachments/assets/f67f1949-f80d-42e3-9c3b-79336e001512)

# fontsplitta

`fontsplitta` is a command-line tool that splits web fonts and generates CSS.

It creates web fonts that are divided into specific Unicode ranges, similar to Google Fonts.

By properly splitting large fonts such as Japanese fonts, it aims to reduce transfer size and improve user experience.

## Installation

Install from Homebrew (macOS):

```console
brew install shunirr/fontsplitta/fontsplitta
```

Install from PyPI:

```console
pip install fontsplitta
```

Or, you can download executables from releases:

- https://github.com/shunirr/fontsplitta/releases

## Development

This project uses [uv](https://github.com/astral-sh/uv) for Python project management.

To set up the development environment:

```console
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/shunirr/fontsplitta.git
cd fontsplitta

# Create virtual environment and install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev

# Activate the virtual environment
source .venv/bin/activate

# Run fontsplitta in development mode
fontsplitta --help
```

To build the project:

```console
# Build distributions
uv build

# Build standalone executable with PyInstaller
uv run pyinstaller --onefile fontsplitta/__main__.py -n fontsplitta
```

## Getting Started

Firstly, generate an `unicode_ranges.txt` using Google Fonts' CSS:

```console
fontsplitta get-unicode-ranges-from-google-fonts
```

Secondly, split fonts and generate CSS:

```console
fontsplitta split FONT_FILE
```

## Using a custom CSS template file

If you want to modify the output CSS, you can create a new template file:

```
@font-face {
  font-family: "${font_family}";
  font-style: ${font_style};
  font-weight: ${font_weight};
  src: url(http://localhost:8080/output/${font_filename}) format("${font_format}");
  unicode-range: ${unicode_range};
}
```

Basically, you should use your environment's hostname in the `src` section.

And then,

```console
fontsplitta split FONT_FILE --css_template=YOUR_CSS_TEMPLATE
```

You can use below variables:

- `font_family` ... The font-family name extracted from the original font file
- `font_style` ... The font style, always returns `normal`
- `font_weight` ... The font weight extracted from the original font file
- `font_filename` ... The split font filename
- `font_format` ... The format of the output font, such as `woff` or `woff2`
- `unicode_range` ... The unicode ranges specified in `unicode_ranges.txt`

## Using custom unicode ranges

If you want to use custom unicode ranges, you can use the `--unicode_ranges_file` option:

```console
fontsplitta split FONT_FILE --unicode_ranges_file=YOUR_UNICODE_RANGES_FILE
```

You can generate the unicode ranges using your web page contents.

## Test with local web server

```console
fontsplitta test-server
```
