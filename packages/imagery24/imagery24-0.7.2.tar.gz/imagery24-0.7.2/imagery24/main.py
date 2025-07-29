from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO
import math

from imagery24.extract import extract_webp_images
from imagery24.georeference import get_gcps
from imagery24.tags import get_metadata
from imagery24.tiff import create_tiff
from imagery24.tiles import get_tiles


def get_levels_bounds(
    metadata: list[dict[bytes, int | str]],
) -> list[tuple[int, int, int, int]]:
    tile_size = 256

    LEVEL_TAGS = {b"PGD_CB", b"PPTY", b"PPTX"}

    try:
        height = int(metadata[0][b"image_height_px"])
        width = int(metadata[0][b"image_width_px"])
    except (KeyError, ValueError):
        raise ValueError("Inable to get image size from metadata")

    layers = []
    zoom = 0

    for level_metadata in metadata[::-1]:
        if LEVEL_TAGS.intersection(level_metadata.keys()):
            x_min = 0
            y_min = 0
            x_max = math.ceil(width / (tile_size * 2**zoom))
            y_max = math.ceil(height / (tile_size * 2**zoom))

            layers.append((x_min, y_min, x_max, y_max))
            zoom += 1

    return layers[::-1]


def convert(input_file: Path | str, output_file: Path | str):
    input_file = Path(input_file)
    output_file = Path(output_file)

    assert input_file.exists(), f"File not found: {input_file}"
    output_dir = output_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_file, "rb") as input_io:
        geotiff_buffer = convert_io(input_io)

        with open(output_file, "wb") as output_io:
            output_io.write(geotiff_buffer.read())

            print(f"GeoTIFF saved to {output_file}")


def convert_io(input_io: BinaryIO) -> BinaryIO:
    metadata = get_metadata(input_io)
    levels_bounds = get_levels_bounds(metadata)
    tiles = list(get_tiles(levels_bounds))

    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        extract_webp_images(input_io, tiles, temp_dir_path)
        max_zoom = len(levels_bounds) - 1

        width = int(metadata[0][b"image_width_px"])
        height = int(metadata[0][b"image_height_px"])
        corner_coords_str = str(metadata[max_zoom][b"PGD_CO"])
        corner_coords = [
            tuple(map(float, coord.split(",")))
            for coord in corner_coords_str.split(" ")
        ]
        corner_coords = corner_coords[:4]
        gcps = get_gcps(corner_coords, width, height)

        return create_tiff(temp_dir_path, levels_bounds, max_zoom, width, height, gcps)
