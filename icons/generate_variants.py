"""
Image variant generator for application deployment.

Generates icon and image variants from a master source file for multiple
platforms: Electron (Windows/macOS), iOS, web favicons, PWA, and social preview.

Args (CLI, all optional):
    --source: Path to source image (default: auto-detect master.*)
    --output: Output directory (default: same folder as the script)
    --targets: Comma-separated target list (default: web-favicon, og-image)
    --ios: Also generate iOS app icon ladder (sugar for --targets +ios)
    --yes: Skip interactive prompts, generate the default target set

Returns:
    Generated image files in output directory, organised by target

Dependencies:
    - Inkscape (for SVG source files - must be in PATH)
    - Pillow (pip install Pillow)

Usage:
    python3 generate_variants.py              # Interactive mode
    python3 generate_variants.py --yes        # Default set (web + og-image)
    python3 generate_variants.py --yes --ios  # Default set + iOS ladder
    python3 generate_variants.py --targets web-favicon,ios

Convention: see devkit/aesthetics/icons-convention.md. Copy this script into
the target project's icons/ folder (or static/icons/ for Flask) and run.

LLM Note: Copy this script to project folders and modify as needed.
         The script is designed to be self-contained and editable.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required")
    print("Install with: pip install Pillow")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
DEFAULT_OUTPUT_DIR = SCRIPT_DIR
# Default target set when --yes is used without --targets. Matches the
# universal canonical set in devkit/aesthetics/icons-convention.md (web +
# PWA + social). iOS and electron targets are opt-in via --targets or --ios.
DEFAULT_TARGETS = ["web-favicon", "og-image"]

# Supported source file extensions
SOURCE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp"}

# Target definitions: name -> (description, sizes_or_config)
TARGETS = {
    "electron-windows": {
        "description": ".ico with multiple sizes for Windows",
        "sizes": [16, 32, 48, 64, 128, 256],
        "output_format": "ico",
    },
    "electron-macos": {
        "description": ".icns with multiple sizes for macOS",
        "sizes": [16, 32, 64, 128, 256, 512, 1024],
        "output_format": "icns",
    },
    "ios": {
        "description": "App icons for iOS (76px - 1024px)",
        "sizes": [76, 120, 152, 167, 180, 1024],
        "output_format": "png",
        "naming": "Icon-{size}.png",
    },
    "web-favicon": {
        "description": "Favicons, apple-touch, PWA icons",
        "components": {
            "favicon.ico": [16, 32, 48],
            "apple-touch-icon.png": [180],
            "icon-192.png": [192],
            "icon-512.png": [512],
        },
    },
    "og-image": {
        "description": "Social preview image (1200x630)",
        "size": (1200, 630),
        "output_format": "png",
    },
}


# =============================================================================
# INKSCAPE HANDLING
# =============================================================================


def find_inkscape():
    """
    Locate Inkscape executable.

    Args: None
    Returns: Path to Inkscape executable, or None if not found
    """
    inkscape_paths = [
        "inkscape",
        "/usr/bin/inkscape",
        "/Applications/Inkscape.app/Contents/MacOS/inkscape",
        r"C:\Program Files\Inkscape\bin\inkscape.exe",
        r"C:\Program Files\Inkscape\inkscape.exe",
    ]
    for path in inkscape_paths:
        if shutil.which(path):
            return path
        if Path(path).exists():
            return path
    return None


def svg_to_png(inkscape_path, svg_path, output_path, width, height=None):
    """
    Convert SVG to PNG at specified size using Inkscape.

    Args:
        inkscape_path: Path to Inkscape executable
        svg_path: Path to source SVG file
        output_path: Path for output PNG file
        width: Output width in pixels
        height: Output height in pixels (default: same as width)

    Returns: True if successful, False otherwise
    """
    if height is None:
        height = width

    cmd = [
        inkscape_path,
        str(svg_path),
        "--export-filename",
        str(output_path),
        "--export-width",
        str(width),
        "--export-height",
        str(height),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


# =============================================================================
# IMAGE PROCESSING (IN-MEMORY)
# =============================================================================


def load_source_image(source_path):
    """
    Load source image and convert to appropriate mode.

    Args:
        source_path: Path to source image

    Returns: PIL Image object, or None on failure
    """
    try:
        img = Image.open(source_path)
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            return img.convert("RGBA")
        return img.convert("RGB")
    except Exception as e:
        print(f"    Error loading image: {e}")
        return None


def resize_in_memory(img, width, height=None):
    """
    Resize a PIL Image in memory.

    Args:
        img: PIL Image object
        width: Output width in pixels
        height: Output height in pixels (default: same as width)

    Returns: Resized PIL Image object
    """
    if height is None:
        height = width
    return img.resize((width, height), Image.Resampling.LANCZOS)


def svg_to_pil(inkscape_path, svg_path, width, height=None):
    """
    Convert SVG to PIL Image using Inkscape and system temp directory.

    Args:
        inkscape_path: Path to Inkscape executable
        svg_path: Path to source SVG file
        width: Output width in pixels
        height: Output height in pixels (default: same as width)

    Returns: PIL Image object, or None on failure
    """
    if height is None:
        height = width

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        cmd = [
            inkscape_path,
            str(svg_path),
            "--export-filename",
            str(tmp_path),
            "--export-width",
            str(width),
            "--export-height",
            str(height),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and tmp_path.exists():
            img = Image.open(tmp_path)
            img.load()  # Force load before we delete the file
            return img
        return None
    except Exception:
        return None
    finally:
        tmp_path.unlink(missing_ok=True)


def create_ico_from_images(images, output_path):
    """
    Create multi-size .ico file from PIL Image objects.

    Args:
        images: List of PIL Image objects (different sizes)
        output_path: Path for output .ico file

    Returns: True if successful, False otherwise
    """
    if not images:
        return False
    try:
        images[0].save(output_path, format="ICO", sizes=[(img.width, img.height) for img in images], append_images=images[1:])
        return True
    except Exception:
        return False


def create_icns_from_images(images_dict, output_path):
    """
    Create .icns file for macOS from PIL Image objects.

    Args:
        images_dict: Dict mapping size -> PIL Image object
        output_path: Path for output .icns file

    Returns: True if successful, False otherwise

    LLM Note: Uses iconutil on macOS. On other platforms, creates .iconset
              folder that can be converted on a Mac later.
    """
    iconset_dir = output_path.parent / "icon.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # macOS iconset naming convention
    iconset_names = {
        16: ["icon_16x16.png"],
        32: ["icon_16x16@2x.png", "icon_32x32.png"],
        64: ["icon_32x32@2x.png"],
        128: ["icon_128x128.png"],
        256: ["icon_128x128@2x.png", "icon_256x256.png"],
        512: ["icon_256x256@2x.png", "icon_512x512.png"],
        1024: ["icon_512x512@2x.png"],
    }

    for size, names in iconset_names.items():
        if size in images_dict:
            for name in names:
                images_dict[size].save(iconset_dir / name)

    # Try to create .icns using iconutil (macOS only)
    if shutil.which("iconutil"):
        try:
            result = subprocess.run(["iconutil", "-c", "icns", str(iconset_dir), "-o", str(output_path)], capture_output=True, timeout=30)
            if result.returncode == 0:
                shutil.rmtree(iconset_dir)
                return True
        except Exception:
            pass

    print(f"    Note: .iconset folder created at {iconset_dir}")
    print("    Run 'iconutil -c icns icon.iconset -o icon.icns' on macOS to create .icns")
    return True


# =============================================================================
# SOURCE FILE DETECTION
# =============================================================================


def get_file_modified_date(file_path):
    """
    Get file modification date formatted as "d Month yyyy".

    Args:
        file_path: Path to file

    Returns: Formatted date string, e.g. "5 January 2026"
    """
    mtime = file_path.stat().st_mtime
    dt = datetime.fromtimestamp(mtime)
    # Use f-string to avoid platform-specific strftime codes (%-d on Linux, %#d on Windows)
    return f"{dt.day} {dt.strftime('%B %Y')}"


def find_master_files(directory):
    """
    Find all master.* files in directory.

    Args:
        directory: Path to search in

    Returns: List of Path objects for master files found
    """
    masters = []
    for ext in SOURCE_EXTENSIONS:
        pattern = f"master{ext}"
        matches = list(directory.glob(pattern))
        masters.extend(matches)
    return sorted(masters)


def find_all_image_files(directory):
    """
    Find all supported image files in directory.

    Args:
        directory: Path to search in

    Returns: List of Path objects for image files found
    """
    images = []
    for ext in SOURCE_EXTENSIONS:
        images.extend(directory.glob(f"*{ext}"))
    return sorted(set(images))


def prompt_for_source(directory):
    """
    Interactively prompt user to select source file.

    Args:
        directory: Path to search for files

    Returns: Path to selected source file, or None if cancelled
    """
    masters = find_master_files(directory)

    if len(masters) == 1:
        # Single master file found - confirm
        mod_date = get_file_modified_date(masters[0])
        print(f"\nFound source: {masters[0].name} (last updated {mod_date})")
        response = input("Use this file? [Y/n, Enter = Yes]: ").strip().lower()
        if response in ("", "y", "yes"):
            return masters[0]

    if len(masters) > 1:
        # Multiple master files - ask which one
        print("\nMultiple master files found:")
        for i, f in enumerate(masters, 1):
            print(f"  {i}. {f.name}")
        print(f"  {len(masters) + 1}. Choose a different file")

        while True:
            choice = input(f"Select [1-{len(masters) + 1}]: ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(masters):
                    return masters[idx - 1]
                if idx == len(masters) + 1:
                    break
            print("Invalid selection, try again.")

    # No master files or user wants different file - show all images
    all_images = find_all_image_files(directory)
    if not all_images:
        print("\nNo image files found in directory.")
        path = input("Enter path to source file: ").strip()
        if path and Path(path).exists():
            return Path(path)
        return None

    print("\nAvailable image files:")
    for i, f in enumerate(all_images, 1):
        print(f"  {i}. {f.name}")

    while True:
        choice = input(f"Select [1-{len(all_images)}] or enter path: ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(all_images):
                return all_images[idx - 1]
        elif Path(choice).exists():
            return Path(choice)
        print("Invalid selection, try again.")


# =============================================================================
# TARGET GENERATION (IN-MEMORY)
# =============================================================================


def get_resized_images(source_path, sizes, inkscape_path=None):
    """
    Generate resized images in memory for multiple sizes.

    Args:
        source_path: Path to source image (SVG or raster)
        sizes: List of sizes to generate
        inkscape_path: Path to Inkscape (required for SVG sources)

    Returns: Dict mapping size -> PIL Image object
    """
    is_svg = source_path.suffix.lower() == ".svg"
    images = {}

    if is_svg:
        # SVG: use Inkscape for each size (uses system temp internally)
        if not inkscape_path:
            print("    Inkscape required for SVG")
            return images
        for size in sizes:
            img = svg_to_pil(inkscape_path, source_path, size)
            if img:
                images[size] = img
    else:
        # Raster: load once, resize in memory
        source_img = load_source_image(source_path)
        if not source_img:
            return images
        for size in sizes:
            images[size] = resize_in_memory(source_img, size)

    return images


def generate_electron_windows(source_path, output_dir, inkscape_path):
    """
    Generate Windows .ico file.

    Args:
        source_path: Path to source image
        output_dir: Directory for output
        inkscape_path: Path to Inkscape (for SVG)

    Returns: True if successful
    """
    print("  Generating electron-windows...")
    config = TARGETS["electron-windows"]
    sizes = config["sizes"]

    images = get_resized_images(source_path, sizes, inkscape_path)
    if not images:
        print("    FAILED - no images generated")
        return False

    ico_path = output_dir / "icon.ico"
    # Create list of images sorted by size for .ico
    image_list = [images[s] for s in sorted(images.keys())]
    success = create_ico_from_images(image_list, ico_path)

    if success:
        print(f"    Created: icon.ico ({', '.join(str(s) for s in sizes)}px)")
    else:
        print("    FAILED to create .ico")

    return success


def generate_electron_macos(source_path, output_dir, inkscape_path):
    """
    Generate macOS .icns file.

    Args:
        source_path: Path to source image
        output_dir: Directory for output
        inkscape_path: Path to Inkscape (for SVG)

    Returns: True if successful
    """
    print("  Generating electron-macos...")
    config = TARGETS["electron-macos"]
    sizes = config["sizes"]

    images = get_resized_images(source_path, sizes, inkscape_path)
    if not images:
        print("    FAILED - no images generated")
        return False

    icns_path = output_dir / "icon.icns"
    success = create_icns_from_images(images, icns_path)

    return success


def generate_ios(source_path, output_dir, inkscape_path):
    """
    Generate iOS app icons.

    Args:
        source_path: Path to source image
        output_dir: Directory for output
        inkscape_path: Path to Inkscape (for SVG)

    Returns: True if successful
    """
    print("  Generating ios...")
    config = TARGETS["ios"]
    sizes = config["sizes"]

    output_dir.mkdir(parents=True, exist_ok=True)

    images = get_resized_images(source_path, sizes, inkscape_path)
    if not images:
        print("    FAILED - no images generated")
        return False

    for size, img in images.items():
        output_path = output_dir / f"Icon-{size}.png"
        img.save(output_path)

    print(f"    Created: {len(images)}/{len(sizes)} iOS icons")
    return len(images) > 0


def generate_web_favicon(source_path, output_dir, inkscape_path):
    """
    Generate web favicons and PWA icons.

    Args:
        source_path: Path to source image
        output_dir: Directory for output
        inkscape_path: Path to Inkscape (for SVG)

    Returns: True if successful
    """
    print("  Generating web-favicon...")
    config = TARGETS["web-favicon"]

    output_dir.mkdir(parents=True, exist_ok=True)

    is_svg = source_path.suffix.lower() == ".svg"
    generated_files = []

    # Copy SVG as favicon.svg if source is SVG
    if is_svg:
        svg_dest = output_dir / "favicon.svg"
        shutil.copy(source_path, svg_dest)
        generated_files.append("favicon.svg")

    # Collect all sizes needed
    all_sizes = set()
    for sizes in config["components"].values():
        all_sizes.update(sizes)

    images = get_resized_images(source_path, list(all_sizes), inkscape_path)
    if not images:
        print("    FAILED - no images generated")
        return len(generated_files) > 0

    # Generate favicon.ico
    ico_sizes = config["components"]["favicon.ico"]
    ico_images = [images[s] for s in ico_sizes if s in images]
    if ico_images:
        ico_path = output_dir / "favicon.ico"
        if create_ico_from_images(ico_images, ico_path):
            generated_files.append("favicon.ico")

    # Generate other components (single-size PNGs)
    other_components = {k: v for k, v in config["components"].items() if k != "favicon.ico"}
    for filename, sizes in other_components.items():
        size = sizes[0]
        if size in images:
            output_path = output_dir / filename
            images[size].save(output_path)
            generated_files.append(filename)

    print(f"    Created: {', '.join(generated_files)}")
    return len(generated_files) > 0


def generate_og_image(source_path, output_dir, inkscape_path):
    """
    Generate Open Graph social preview image.

    Args:
        source_path: Path to source image
        output_dir: Directory for output
        inkscape_path: Path to Inkscape (for SVG)

    Returns: True if successful

    LLM Note: OG images are 1200x630 (not square). Source image is centred
              and scaled to fit, with transparent/white background fill.
    """
    print("  Generating og-image...")
    config = TARGETS["og-image"]
    width, height = config["size"]

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "og-image.png"

    is_svg = source_path.suffix.lower() == ".svg"

    try:
        # Get source as PIL Image
        if is_svg:
            if not inkscape_path:
                print("    FAILED - Inkscape required for SVG")
                return False
            source_img = svg_to_pil(inkscape_path, source_path, 1024)
            if not source_img:
                print("    FAILED to convert SVG")
                return False
        else:
            source_img = load_source_image(source_path)
            if not source_img:
                return False

        # Create output canvas
        if source_img.mode == "RGBA":
            canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        else:
            canvas = Image.new("RGB", (width, height), (255, 255, 255))

        # Scale source to fit within canvas (maintain aspect ratio)
        src_w, src_h = source_img.size
        scale = min(width / src_w, height / src_h) * 0.8  # 80% of available space
        new_w = int(src_w * scale)
        new_h = int(src_h * scale)

        resized = source_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Centre on canvas
        x = (width - new_w) // 2
        y = (height - new_h) // 2

        if resized.mode == "RGBA":
            canvas.paste(resized, (x, y), resized)
        else:
            canvas.paste(resized, (x, y))

        canvas.save(output_path)

        print(f"    Created: og-image.png ({width}x{height})")
        return True

    except Exception as e:
        print(f"    FAILED: {e}")
        return False


# =============================================================================
# OUTPUT FILE MANAGEMENT
# =============================================================================


def get_target_outputs(target):
    """
    Get list of output filenames for a target.

    Args:
        target: Target name (e.g. "ios", "web-favicon")

    Returns: List of filenames (not paths) that this target generates
    """
    outputs = {
        "electron-windows": ["icon.ico"],
        "electron-macos": ["icon.icns", "icon.iconset"],  # iconset only on non-Mac
        "ios": [f"Icon-{s}.png" for s in [76, 120, 152, 167, 180, 1024]],
        "web-favicon": ["favicon.ico", "favicon.svg", "apple-touch-icon.png", "icon-192.png", "icon-512.png"],
        "og-image": ["og-image.png"],
    }
    return outputs.get(target, [])


def find_existing_outputs(output_dir, targets):
    """
    Find existing files/folders in output_dir that would be created by targets.

    Args:
        output_dir: Path to output directory
        targets: List of target names

    Returns: List of Path objects for existing files/folders
    """
    existing = []
    if not output_dir.exists():
        return existing

    for target in targets:
        for filename in get_target_outputs(target):
            path = output_dir / filename
            if path.exists() or path.is_dir():
                existing.append(path)

    return existing


def delete_outputs(output_dir, targets):
    """
    Delete existing output files/folders for specified targets.

    Args:
        output_dir: Path to output directory
        targets: List of target names

    Returns: Number of items deleted
    """
    deleted = 0
    for target in targets:
        for filename in get_target_outputs(target):
            path = output_dir / filename
            if path.is_dir():
                shutil.rmtree(path)
                deleted += 1
            elif path.exists():
                path.unlink()
                deleted += 1
    return deleted


# =============================================================================
# MAIN FLOW
# =============================================================================


def prompt_for_targets():
    """
    Interactively prompt user to select targets.

    Args: None
    Returns: List of target names to generate
    """
    print("\nAvailable targets:")
    target_list = list(TARGETS.keys())
    for i, name in enumerate(target_list, 1):
        desc = TARGETS[name]["description"]
        print(f"  {i}. {name:20} {desc}")

    while True:
        choice = input("\nSelect targets (comma-separated, e.g. 1,3,4) [Enter = all]: ").strip()

        # Enter = all targets
        if choice == "":
            return target_list

        if choice.lower() == "a" or choice.lower() == "all":
            return target_list

        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            selected = []
            for idx in indices:
                if 1 <= idx <= len(target_list):
                    selected.append(target_list[idx - 1])
            if selected:
                return selected
        except ValueError:
            pass

        print("Invalid selection, try again.")


def main():
    """
    Main entry point.

    Args: None (uses CLI arguments)
    Returns: Exit code (0 success, 1 failure)
    """
    parser = argparse.ArgumentParser(description="Generate image variants for deployment")
    parser.add_argument("--source", help="Path to source image")
    parser.add_argument("--output", help="Output directory", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--targets", help="Comma-separated targets (e.g. web-favicon,ios)")
    parser.add_argument("--ios", action="store_true", help="Also include the iOS app icon ladder (sugar for adding 'ios' to default targets)")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip prompts; generate default target set (web-favicon + og-image)")

    args = parser.parse_args()

    print("=" * 50)
    print("Image Variant Generator")
    print("=" * 50)

    # Check for Inkscape
    inkscape_path = find_inkscape()
    if inkscape_path:
        print(f"Inkscape: {inkscape_path}")
    else:
        print("Inkscape: Not found (SVG sources will not work)")

    # Determine source file
    if args.source:
        source_path = Path(args.source)
        if not source_path.exists():
            print(f"\nERROR: Source file not found: {source_path}")
            return 1
    elif args.yes:
        # Auto mode - find single master file
        masters = find_master_files(SCRIPT_DIR)
        if len(masters) == 1:
            source_path = masters[0]
            print(f"\nSource: {source_path.name}")
        else:
            print("\nERROR: --yes requires exactly one master.* file (or use --source)")
            return 1
    else:
        # Interactive mode
        source_path = prompt_for_source(SCRIPT_DIR)
        if not source_path:
            print("\nNo source file selected. Exiting.")
            return 1

    # Validate source
    if source_path.suffix.lower() == ".svg" and not inkscape_path:
        print("\nERROR: SVG source requires Inkscape. Please install from https://inkscape.org/")
        return 1

    # Determine output directory
    output_dir = Path(args.output)
    print(f"Output: {output_dir}/")

    # Determine targets
    if args.targets:
        selected_targets = [t.strip() for t in args.targets.split(",")]
        invalid = [t for t in selected_targets if t not in TARGETS]
        if invalid:
            print(f"\nERROR: Unknown targets: {', '.join(invalid)}")
            print(f"Valid targets: {', '.join(TARGETS.keys())}")
            return 1
    elif args.yes:
        selected_targets = list(DEFAULT_TARGETS)
        print(f"Targets: default set ({', '.join(selected_targets)})")
    else:
        selected_targets = prompt_for_targets()

    # --ios augments whatever was selected (sugar for the iOS ladder)
    if args.ios and "ios" not in selected_targets:
        selected_targets.append("ios")
        print("Targets: + ios (from --ios flag)")

    # Check for existing files that will be replaced
    existing_files = find_existing_outputs(output_dir, selected_targets)
    if existing_files and not args.yes:
        print(f"\nNote: {len(existing_files)} existing file(s) in output folder will be replaced:")
        for f in existing_files[:10]:  # Show first 10
            print(f"  - {f.name}")
        if len(existing_files) > 10:
            print(f"  ... and {len(existing_files) - 10} more")
        response = input("\nContinue? [Y/n, Enter = Yes]: ").strip().lower()
        if response not in ("", "y", "yes"):
            print("Cancelled.")
            return 0

    # Delete existing outputs before generating (clean slate)
    if existing_files:
        delete_outputs(output_dir, selected_targets)

    print("\n" + "-" * 50)
    print("Generating variants...")
    print("-" * 50 + "\n")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate each target
    generators = {
        "electron-windows": generate_electron_windows,
        "electron-macos": generate_electron_macos,
        "ios": generate_ios,
        "web-favicon": generate_web_favicon,
        "og-image": generate_og_image,
    }

    results = {}
    for target in selected_targets:
        if target in generators:
            results[target] = generators[target](source_path, output_dir, inkscape_path)
        else:
            print(f"  {target}: No generator implemented")
            results[target] = False

    # Summary
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    for target, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  {target:20} {status}")

    success_count = sum(1 for s in results.values() if s)
    print(f"\n{success_count}/{len(results)} targets completed successfully")
    print(f"Output: {output_dir}/")

    return 0 if success_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
