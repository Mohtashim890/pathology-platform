"""Print the key properties of a whole-slide image and save a thumbnail (Lesson L0.3, step 5).

Usage:
    uv run inspect_slide.py <path-to-slide>
"""

import sys
from pathlib import Path

import openslide


def read_mpp(slide: openslide.OpenSlide) -> float | None:
    """Return microns per pixel, or None if the file doesn't say."""
    value = slide.properties.get(openslide.PROPERTY_NAME_MPP_X)
    return float(value) if value is not None else None


def describe(path: Path) -> None:
    with openslide.OpenSlide(str(path)) as slide:
        width, height = slide.dimensions
        mpp = read_mpp(slide)
        vendor = slide.properties.get(openslide.PROPERTY_NAME_VENDOR, "unknown")
        objective = slide.properties.get(openslide.PROPERTY_NAME_OBJECTIVE_POWER, "unknown")

        print(f"File:            {path.name}")
        print(f"Size on disk:    {path.stat().st_size / 1e6:,.1f} MB")
        print(f"Vendor:          {vendor}")
        print(f"Level 0 size:    {width:,} x {height:,} px")
        print(f"Objective power: {objective}")

        if mpp is None:
            print("mpp:             not stored in this file")
        else:
            print(f"mpp:             {mpp:.4f} µm/pixel")
            print(f"Physical size:   {width * mpp / 1000:.1f} x {height * mpp / 1000:.1f} mm")

        uncompressed_gb = width * height * 3 / 1e9
        print(f"Uncompressed:    {uncompressed_gb:,.1f} GB")

        print(f"Pyramid levels:  {slide.level_count}")
        for level in range(slide.level_count):
            level_width, level_height = slide.level_dimensions[level]
            downsample = slide.level_downsamples[level]
            print(f"  level {level}: {level_width:>8,} x {level_height:>8,} px   downsample {downsample:6.2f}")

        names = list(slide.associated_images.keys())
        print(f"Associated images: {', '.join(names) if names else 'none'}")

        thumbnail = slide.get_thumbnail((1024, 1024))
        thumbnail_path = path.with_name(f"{path.stem}_thumbnail.png")
        thumbnail.save(thumbnail_path)
        print(f"Thumbnail saved: {thumbnail_path}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: uv run inspect_slide.py <path-to-slide>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    describe(path)


if __name__ == "__main__":
    main()