<h1 align="center">
  <br>
  <img src="docs/img/resemu.png" alt="resemu" width="200">
  <br>
  resemu
  <br>
</h1>

<h4 align="center">A simple CLI tool to generate clean resumes from YAML data.</h4>

<p align="center">
  <a href="https://pypi.org/project/resemu">
    <img src="https://img.shields.io/pypi/v/resemu?logo=pypi"
        alt="PyPI version">
  </a>
  <a href="https://github.com/matheodrd/resemu/actions/workflows/publish.yml">
    <img src="https://github.com/matheodrd/resemu/actions/workflows/publish.yml/badge.svg"
        alt="CI">
  </a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#example">Example</a> •
  <a href="#installation">Installation</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#cli-usage">CLI Usage</a>
</p>

![screenshot](docs/img/resemu-demo.gif)

---

## Features

- **YAML-based Input:** Define your resume content in a clear, structured YAML file.
- **LaTeX Templates:** Clean and professional resume layouts using LaTeX templates.
- **Rich CLI Experience:** Built with Typer and Rich for user-friendly command-line interactions.
- **Validation:** Data validation using Pydantic ensures your resume data is correct before rendering.
- **Easy to Use:** Simple commands to validate and generate your resume.

## Example

The YAML file in [examples/](examples/john_doe.yml) produces the [following PDF](examples/output/john_doe.pdf) using the *engineering* template :

<div align="center">

<img src="docs/img/pdf-resume.jpg" alt="PDF generated from example YAML data (engineering)" width="400"/>
</div>

## Installation

### LaTeX

You firstly need a LaTeX distribution with extra fonts to use resemu. On Debian :

```bash
sudo apt install texlive texlive-fonts-extra
```

### resemu

You need Python 3.12 or newer.

```bash
pip install resemu
```

Or, if you want the latest development version:

```bash
pip install git+https://github.com/matheodrd/resemu.git
```

## Getting Started

### Prepare Your Resume Data

Start by creating a YAML file describing your background, skills, and experiences. You can use the provided [`examples/john_doe.yml`](examples/john_doe.yml) as a reference for the expected structure and fields.

> **Tip:** resemu provides a JSON schema ([resume_schema.json](schema/resemu.schema.json)) to help you edit your YAML file with autocompletion and validation in your IDE.

### Generate Your PDF Resume

Once your YAML is ready, generate a PDF with:

```bash
resemu generate -t engineering -o my_resume.pdf my_resume.yml
```

- `-t, --template` lets you pick the desired template (default: `engineering`)
- `-o, --output` sets the output PDF filename

### Validate Your YAML

Before generating, you can check your YAML file for errors or missing fields:

```bash
resemu validate my_resume.yml
```

The CLI will let you know about any structural issues or missing required data.

## CLI Usage

### `resemu`

```console
$ resemu [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `generate`: Generate a PDF resume from a YAML data file
* `validate`: Validate a YAML resume data file
* `templates`: List available resume templates
* `version`: Show version information

### `resemu generate`

Generate a PDF resume from a YAML data file.

This command processes your YAML resume data and generates a clean PDF using the specified template.

**Usage**:

```console
$ resemu generate [OPTIONS] DATA_FILE
```

**Arguments**:

* `DATA_FILE`: YAML file containing resume data  [required]

**Options**:

* `-t, --template TEXT`: Resume template to use  [default: engineering]
* `-o, --output PATH`: Output file path (defaults to input filename with .pdf extension)
* `-f, --force`: Overwrite existing output file without confirmation
* `--help`: Show this message and exit.

### `resemu validate`

Validate a YAML resume data file.

Checks if your YAML file is properly formatted and contains all required fields.

**Usage**:

```console
$ resemu validate [OPTIONS] DATA_FILE
```

**Arguments**:

* `DATA_FILE`: YAML file to validate  [required]

**Options**:

* `-v, --verbose`: Show detailed validation information
* `--help`: Show this message and exit.

### `resemu templates`

List available resume templates.

Shows all available templates you can use with the generate command.

**Usage**:

```console
$ resemu templates [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `resemu version`

Show version information.

**Usage**:

```console
$ resemu version [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
