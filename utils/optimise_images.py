#!/usr/bin/env python3
"""
Resize and compress photos before they are committed.

Run this on any new photo before adding it to images/. The build copies images/
as-is, so whatever is committed is what visitors download. Phone photos are often
4000px wide and several megabytes; a hero needs about 1600px and a card image
about 800px.

Usage:
  python3 utils/optimise_images.py path/to/photo.jpg [more.jpg ...] [--max-width 1600] [--quality 82] [--out images/]

Writes <name>.jpg (or .png for images with transparency) into --out, never
overwriting the source. Needs Pillow: pip install --user pillow
"""

import argparse
import logging
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install --user pillow")

logger = logging.getLogger(__name__)


def optimise(source: Path, out_dir: Path, max_width: int, quality: int) -> Path:
    """
    Resize one image to at most max_width (keeping aspect ratio) and save it compressed.
    Args: source -- image path; out_dir -- destination folder; max_width -- pixels; quality -- JPEG quality 1-95
    Returns: the written path
    Raises ValueError if the destination would overwrite the source.
    """
    with Image.open(source) as img:
        img = ImageOps.exif_transpose(img)
        has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, round(img.height * ratio)), Image.LANCZOS)
        suffix = ".png" if has_alpha else ".jpg"
        dest = out_dir / (source.stem + suffix)
        if dest.resolve() == source.resolve():
            raise ValueError(f"{source} would be overwritten; choose a different --out")
        out_dir.mkdir(parents=True, exist_ok=True)
        if has_alpha:
            img.convert("RGBA").save(dest, "PNG", optimize=True)
        else:
            img.convert("RGB").save(dest, "JPEG", quality=quality, optimize=True, progressive=True)
    return dest


def main() -> int:
    """
    Parse args and optimise each file, logging before/after sizes.
    Args: none (reads sys.argv)
    Returns: exit code (1 if any file failed)
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Resize and compress photos for the site.")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--max-width", type=int, default=1600)
    parser.add_argument("--quality", type=int, default=82)
    parser.add_argument("--out", type=Path, default=Path("images"))
    args = parser.parse_args()
    if not 1 <= args.quality <= 95 or args.max_width < 100:
        logger.error("--quality must be 1-95 and --max-width at least 100")
        return 1
    failed = False
    for source in args.files:
        if not source.is_file():
            logger.error("Not a file: %s", source)
            failed = True
            continue
        try:
            dest = optimise(source, args.out, args.max_width, args.quality)
        except (OSError, ValueError) as exc:
            logger.error("%s: %s", source, exc)
            failed = True
            continue
        logger.info("%s (%d KB) -> %s (%d KB)", source, source.stat().st_size // 1024, dest, dest.stat().st_size // 1024)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
