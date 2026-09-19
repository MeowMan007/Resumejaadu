"""
apps/generator/compiler.py

Sandboxed LaTeX → PDF compilation.

Security measures:
  - `-no-shell-escape`      : blocks \\write18 and shell injection
  - `-interaction=nonstopmode -halt-on-error` : fail fast, no interactive prompts
  - `timeout=20`            : hard kill after 20 seconds
  - Runs in a tempdir       : cleaned up on success or failure
  - Non-root user in Docker : see Dockerfile.worker
"""
import pathlib
import shutil
import subprocess
import tempfile
import logging

logger = logging.getLogger(__name__)


class LatexCompileError(Exception):
    """Raised when LaTeX compilation fails."""
    def __init__(self, log_excerpt: str = ""):
        self.log_excerpt = log_excerpt
        super().__init__(f"LaTeX compilation failed.\n{log_excerpt}")


def compile_tex_to_pdf(
    tex_source: str,
    engine: str,
    asset_dir: pathlib.Path,
    runs: int = 2,
    timeout: int = 120,
) -> pathlib.Path:
    """
    Compile a LaTeX source string into a PDF using the specified engine.

    Args:
        tex_source:  Complete LaTeX source text (already rendered from Jinja2)
        engine:      One of 'pdflatex', 'xelatex', 'lualatex'
        asset_dir:   Directory containing .cls, .sty, font files, etc.
        runs:        Number of compilation passes (2 = resolves cross-refs)
        timeout:     Max seconds per pass before SIGKILL

    Returns:
        pathlib.Path pointing to the generated PDF inside a temp directory.
        **Caller is responsible for copying this before the tempdir is cleaned.**

    Raises:
        LatexCompileError: if any pass fails or the PDF does not exist after compilation
    """
    if engine not in ("pdflatex", "xelatex", "lualatex"):
        raise ValueError(f"Unsupported LaTeX engine: {engine!r}")

    # Validate engine is on PATH (use refreshed PATH on Windows)
    safe = _safe_env()
    if not shutil.which(engine, path=safe.get("PATH")):
        raise LatexCompileError(
            f"LaTeX engine '{engine}' not found on PATH. "
            "Is TeX Live / MiKTeX installed?"
        )

    with tempfile.TemporaryDirectory(prefix="resumejaadu_") as workdir:
        work = pathlib.Path(workdir)

        # Copy all template assets (cls, sty, fonts, images) into the work dir
        if asset_dir.exists():
            for item in asset_dir.iterdir():
                dest = work / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

        # Write the rendered .tex source
        tex_path = work / "resume.tex"
        tex_path.write_text(tex_source, encoding="utf-8")

        cmd = [
            engine,
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-no-shell-escape",           # SECURITY: block \write18
            "-output-directory", workdir,
            str(tex_path),
        ]

        last_log = ""
        for pass_num in range(1, runs + 1):
            logger.info(f"LaTeX pass {pass_num}/{runs} using {engine}")
            result = subprocess.run(
                cmd,
                cwd=workdir,
                capture_output=True,
                timeout=timeout,
                text=True,
                env={
                    **_safe_env(),
                    "TEXMFHOME": workdir,
                },
            )
            last_log = (result.stdout or "") + (result.stderr or "")

            if result.returncode != 0:
                log_excerpt = last_log[-3000:]
                logger.error(f"LaTeX failed on pass {pass_num}:\n{log_excerpt}")
                raise LatexCompileError(log_excerpt)

        pdf_path = work / "resume.pdf"
        if not pdf_path.exists():
            raise LatexCompileError("Compilation reported success but PDF not found.")

        # Copy PDF to a sibling temp file that survives past TemporaryDirectory cleanup
        import uuid
        output_path = pathlib.Path(tempfile.gettempdir()) / f"resume_{uuid.uuid4().hex}.pdf"
        shutil.copy2(pdf_path, output_path)
        logger.info(f"PDF generated successfully: {output_path}")
        return output_path


def _safe_env() -> dict:
    """Return a minimal environment for the LaTeX subprocess."""
    import os
    import platform

    # Pass through PATH and HOME so TeX Live / MiKTeX can find fonts/packages
    safe_keys = {"PATH", "HOME", "TMPDIR", "TEMP", "TMP", "TEXMFHOME", "FONTCONFIG_PATH",
                 "USERPROFILE", "APPDATA", "LOCALAPPDATA", "SYSTEMROOT", "WINDIR"}
    env = {k: v for k, v in os.environ.items() if k in safe_keys}

    # On Windows, refresh PATH from registry in case MiKTeX was installed after
    # the Django process started
    if platform.system() == "Windows":
        import subprocess as _sp
        try:
            machine_path = _sp.run(
                ["powershell", "-NoProfile", "-Command",
                 '[Environment]::GetEnvironmentVariable("Path","Machine")'],
                capture_output=True, text=True, timeout=5
            ).stdout.strip()
            user_path = _sp.run(
                ["powershell", "-NoProfile", "-Command",
                 '[Environment]::GetEnvironmentVariable("Path","User")'],
                capture_output=True, text=True, timeout=5
            ).stdout.strip()
            env["PATH"] = f"{machine_path};{user_path}"
        except Exception:
            pass  # Fall back to inherited PATH

    return env


def generate_thumbnail(pdf_path: pathlib.Path, output_path: pathlib.Path, dpi: int = 120) -> bool:
    """
    Generate a PNG thumbnail of the first page of a PDF using poppler's pdftoppm.

    Args:
        pdf_path:    Path to the source PDF
        output_path: Desired output PNG path (e.g. /tmp/thumb.png)
        dpi:         Resolution in dots per inch (120 is fine for thumbnails)

    Returns:
        True on success, False if pdftoppm is not available or fails
    """
    if not shutil.which("pdftoppm"):
        logger.warning("pdftoppm not found — skipping thumbnail generation")
        return False

    # pdftoppm writes <stem>-1.png for page 1
    stem = output_path.stem
    out_dir = output_path.parent

    try:
        result = subprocess.run(
            [
                "pdftoppm",
                "-r", str(dpi),
                "-png",
                "-singlefile",
                str(pdf_path),
                str(out_dir / stem),
            ],
            capture_output=True,
            timeout=30,
            text=True,
        )
        if result.returncode != 0:
            logger.warning(f"pdftoppm failed: {result.stderr}")
            return False

        # pdftoppm creates <stem>.png in -singlefile mode
        generated = out_dir / f"{stem}.png"
        if generated.exists():
            generated.rename(output_path)
            return True
        return False

    except subprocess.TimeoutExpired:
        logger.warning("pdftoppm timed out")
        return False
