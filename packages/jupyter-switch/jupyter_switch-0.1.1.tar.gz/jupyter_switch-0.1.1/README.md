# Jupyter Switch

A command-line tool to convert between Markdown (.md) and Jupyter Notebook (.ipynb) formats.

## Features

- **Automatic detection**: Automatically detects whether the input file is `.md` or `.ipynb` and converts accordingly
- **Bidirectional conversion**: Convert from Markdown to Jupyter Notebook and vice versa
- **Backup protection**: Automatically creates backups when output files already exist
- **Preserves structure**: Maintains code blocks, markdown content, and cell structure

## Installation

Install the package using pip:

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

## Usage

The main command is `jupyter-switch`:

```bash
# Convert a Markdown file to Jupyter Notebook
jupyter-switch example.md

# Convert a Jupyter Notebook to Markdown
jupyter-switch example.ipynb
```

### Examples

```bash
# Convert README.md to README.ipynb
jupyter-switch README.md

# Convert notebook.ipynb to notebook.md
jupyter-switch notebook.ipynb
```

The tool will automatically:
- Detect the input file format
- Generate the appropriate output filename
- Create a backup if the output file already exists
- Convert the content while preserving structure

## Help

```bash
jupyter-switch --help
jupyter-switch --version
```

## Conversion Details

### Markdown to Jupyter Notebook
- Python code blocks (```python...```) become code cells
- All other content becomes markdown cells
- Adds appropriate notebook metadata and structure

### Jupyter Notebook to Markdown  
- Code cells become Python code blocks
- Markdown cells are preserved as-is
- Cell outputs are ignored during conversion

## Requirements

- Python >= 3.10

## License

MIT License
