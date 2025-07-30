from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import shutil


class PDFCompilationError(Exception):
    """Exception raised when PDF compilation fails."""


def compile_pdf(latex_content: str, output_path: str | Path) -> Path:
    """Compile LaTeX content to a PDF file.

    Args:
        latex_content (str): LaTeX content to compile
        output_path (str | Path): PDF file's output path

    Raises:
        PDFCompilationError: If compilation fails

    Returns:
        Path: Path of the generated PDF file
    """
    if not is_pdflatex_available():
        raise PDFCompilationError(
            "The `pdflatex` command is not available on the system. "
            "Install a LaTeX distribution (TeX Live, MiKTeX, etc.)"
        )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        tex_file = temp_dir_path / "resume.tex"

        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(latex_content)

        # Run pdflatex twice: the first pass generates the auxiliary files (.aux, .toc, etc.),
        # and the second pass uses those files to resolve cross-references, update the table of contents,
        # and ensure that all numbered elements (sections, figures, tables) are correctly rendered.
        try:
            for i in range(2):
                result = subprocess.run(
                    [
                        "pdflatex",
                        "-interaction=nonstopmode",
                        "-output-directory",
                        str(temp_dir_path),
                        str(tex_file),
                    ],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir_path,
                )

                if result.returncode != 0:
                    raise PDFCompilationError(
                        f"Failed to compile LaTeX (pass #{i + 1}:\n)"
                        f"Return Code: {result.returncode}\n"
                        f"Error: {result.stderr}\n"
                        f"Log: {result.stdout}\n"
                    )

            pdf_temp = temp_dir_path / "resume.pdf"
            if not pdf_temp.exists():
                raise PDFCompilationError("Generated PDF file cannot be found.")

            shutil.copy2(pdf_temp, output_path)

            return output_path

        except Exception as e:
            if isinstance(e, PDFCompilationError):
                raise
            raise PDFCompilationError(f"Failed to compile LaTeX to PDF: {str(e)}")


def is_pdflatex_available() -> bool:
    """Check if the `pdflatex` command is available on the system."""
    try:
        result = subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
