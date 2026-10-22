"""
Prepare the build output directory and copy static assets into it.

Single responsibility: filesystem housekeeping for _site/ -- clearing and
recreating it, and copying css/, js/, images/ and any repo-root *.pdf
verbatim.
Does not touch page HTML, which build.py writes separately.
"""

import logging
import shutil
import time
from pathlib import Path

from build.errors import BuildError

logger = logging.getLogger(__name__)

_SKIP_NAMES = {".DS_Store", "Thumbs.db"}
_ASSET_DIRS = ("css", "js", "images")


def _should_skip(path: Path) -> bool:
    """
    Report whether a file should be excluded from the asset copy.

    Args:
        path: candidate file path.

    Returns:
        True if the file is a *.tmp.* file or a known junk filename.
    """
    if path.name in _SKIP_NAMES:
        return True
    if ".tmp." in path.name:
        return True
    return False


def prepare_output(out_dir: Path) -> None:
    """
    Delete and recreate the build output directory.

    Args:
        out_dir: build output directory (_site/ by default).

    Returns:
        None.
    """
    # When the repo sits inside a synced folder (Dropbox, OneDrive), the sync
    # client briefly locks files it has just noticed, so deleting the previous
    # build can hit a transient PermissionError. Retry a few times, then fail
    # loudly. Hosted builds (GitHub Actions) never hit this.
    attempts = 6
    for attempt in range(1, attempts + 1):
        if not out_dir.exists():
            break
        try:
            shutil.rmtree(out_dir)
        except PermissionError as exc:
            if attempt == attempts:
                raise BuildError(
                    f"Could not remove {out_dir} after {attempts} attempts (a sync client "
                    f"may be holding a lock): {exc}"
                ) from exc
            logger.info("Output folder locked (attempt %d of %d), retrying", attempt, attempts)
            time.sleep(0.5 * attempt)
    out_dir.mkdir(parents=True)
    logger.info("Prepared clean output directory %s", out_dir)


def copy_assets(root: Path, out_dir: Path) -> None:
    """
    Copy css/, js/, images/ and repo-root *.pdf into the output.

    Args:
        root: repository root Path.
        out_dir: build output directory (_site/).

    Returns:
        None. Skips *.tmp.* files, .DS_Store and Thumbs.db.
    """
    for dir_name in _ASSET_DIRS:
        source_dir = root / dir_name
        if not source_dir.exists():
            continue
        dest_dir = out_dir / dir_name
        shutil.copytree(
            source_dir,
            dest_dir,
            ignore=lambda directory, names: [
                name for name in names if _should_skip(Path(directory) / name)
            ],
        )
        logger.info("Copied %s/ to output", dir_name)

    # Documents kept at the repo root publish at the site root, so a PDF's
    # address (eg /disclosure.pdf) stays fixed for anything linking to it.
    for pdf_path in sorted(root.glob("*.pdf")):
        shutil.copy2(pdf_path, out_dir / pdf_path.name)
        logger.info("Copied %s to output", pdf_path.name)
