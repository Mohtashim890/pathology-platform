"""Whole-slide image size calculator (Lesson L0.3, step 4)."""

BYTES_PER_PIXEL = 3  # one byte each for red, green and blue


def pixels_from_mm(size_mm: float, mpp: float) -> int:
    """Convert a physical length in millimetres to level-0 pixels."""
    microns = size_mm * 1000
    return round(microns / mpp)


def describe_slide(name: str, width_mm: float, height_mm: float, mpp: float) -> dict:
    """Return the pixel size and memory size of a slide as a dictionary."""
    width_px = pixels_from_mm(width_mm, mpp)
    height_px = pixels_from_mm(height_mm, mpp)
    pixels = width_px * height_px
    return {
        "name": name,
        "width_px": width_px,
        "height_px": height_px,
        "gigapixels": pixels / 1e9,
        "uncompressed_gb": pixels * BYTES_PER_PIXEL / 1e9,
    }


def main() -> None:
    slides = [
        ("Typical 40x slide", 20, 15, 0.25),
        ("Same tissue at 20x", 20, 15, 0.5),
        ("L0.1 exercise", 25, 18, 0.5),
    ]

    for name, width_mm, height_mm, mpp in slides:
        info = describe_slide(name, width_mm, height_mm, mpp)
        print(
            f"{info['name']:<20}"
            f"{info['width_px']:>8,} x {info['height_px']:>7,} px"
            f"  = {info['gigapixels']:5.2f} gigapixels"
            f"  = {info['uncompressed_gb']:6.2f} GB uncompressed"
        )


if __name__ == "__main__":
    main()