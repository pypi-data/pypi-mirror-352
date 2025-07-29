import sys
from pathlib import Path

import matplotlib.font_manager as fm
import numpy as np
import rasterio
from affine import Affine
from geopandas import GeoDataFrame
from PIL import Image, ImageDraw, ImageFont
from pykml import parser
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from shapely.geometry import Polygon, Point

FONT_PATH = fm.findfont(fm.FontProperties(family="sans serif"))


def color_to_rgb(color: str) -> tuple[int, int, int]:
    """
    Convert a color string to RGB values.
        "color": A color string in the format "#RRGGBB"
    Returns:
        A tuple of red, green, and blue values (0-255)
    """

    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


def _kml_placemarks_to_geodataframe(placemarks: list) -> GeoDataFrame:
    data = []

    for placemark in placemarks:
        try:
            name = placemark.name.text

            # Default color
            color = "000000"

            # Get color from LineStyle
            if hasattr(placemark, "Style") and hasattr(placemark.Style, "LineStyle"):
                color = placemark.Style.LineStyle.color.text

            children = placemark.getchildren()
            if hasattr(placemark, "MultiGeometry"):
                children = placemark.MultiGeometry.getchildren()

            for geometry in children:
                if "Point" in geometry.tag:
                    coords = geometry.coordinates.text.split(",")
                    shape = Point(float(coords[0]), float(coords[1]))

                elif "LineString" in geometry.tag:
                    coords_text = geometry.coordinates.text.split()
                    coords = [
                        list(map(float, coord.split(",")[:2])) for coord in coords_text
                    ]
                    coords = coords + coords[::-1]  # Close the LineString
                    shape = Polygon(coords)

                elif "Polygon" in geometry.tag:
                    coords = (
                        geometry.outerBoundaryIs.LinearRing.coordinates.text.split()
                    )
                    shape = Polygon(
                        [map(float, coord.split(",")[:2]) for coord in coords]
                    )

                else:
                    continue

                data.append(
                    {
                        "name": name,
                        "geometry": shape,
                        "color": f"#{color}",
                    }
                )

        except Exception as e:
            print(f"Unable to parse placemark: {placemark.__dict__}")
            print(e)

    gdf = GeoDataFrame(data)

    # Add WGS 84 CRS
    gdf.crs = "EPSG:4326"

    # Transform geometries to EPSG:3857
    gdf.to_crs("EPSG:3857", inplace=True)

    return gdf


def _parse_kml_to_geodataframe(kml_file: Path) -> GeoDataFrame:
    with open(kml_file) as file:
        doc = parser.parse(file)

    root = doc.getroot()
    placemarks = root.findall(".//{http://www.opengis.net/kml/2.2}Placemark")

    return _kml_placemarks_to_geodataframe(placemarks)


def _draw_text_labels(
    image: Image.Image,
    gdf: GeoDataFrame,
    transform: Affine,
    colum_name: str = "name",
    font_size: int = 24,
    color: str | None = None,
    offset: tuple[int, int] = (0, 0),
):
    """
    Draw text labels from a GeoDataFrame onto a raster image.

    Args:
        image: A Pillow Image object
        gdf: A GeoDataFrame containing geometries to draw and the text column
        colum_name: The column name containing text to draw
        font_size: The font size for the text labels
        color: The color for the text labels in the format "#RRGGBB"
        offset: A tuple of x and y pixel offsets for the text labels

    Returns:
        None
    """

    draw = ImageDraw.Draw(image)

    for _, row in gdf.iterrows():
        # Calculate text position (centroid of geometry)
        centroid = row.geometry.centroid
        text = str(row[colum_name])
        x, y = ~transform * (centroid.x, centroid.y)
        x += offset[0]
        y += offset[1]

        if color is not None:
            red, green, blue = color_to_rgb(color)
        else:
            red, green, blue = color_to_rgb(str(row["color"]))

        # Adjust font size based on geometry width
        font = ImageFont.truetype(FONT_PATH, font_size)
        text_width = font.getlength(text)

        draw.text(
            (x - text_width // 2, y - font.size // 2),
            text,
            fill=(red, green, blue, 255),
            font=font,
            stroke_width=0.1,
            stroke_fill=(0, 0, 0, 255),
        )


def _draw_geomteries(
    gdf: GeoDataFrame,
    resolution: float = 0.5,
    outline_width: int = 4,
) -> Image.Image:
    """
    Draw geometries from a GeoDataFrame onto a raster image.

    Args:
        gdf: A GeoDataFrame containing geometries to draw and the color column
             with hex colors in the format "#RRGGBB"
        resolution: The output raster resolution in meters
        outline_width: The width of the geometry outline in pixels

    Returns:
        An RGBA raster image
    """

    # Define the output raster dimensions and bounds
    max_test_width = gdf["text_width"].max()
    buffer_width = outline_width * resolution / 2
    boundary = gdf.geometry.buffer(buffer_width + max_test_width)
    bounds = boundary.total_bounds
    width = int((bounds[2] - bounds[0]) / resolution)
    height = int((bounds[3] - bounds[1]) / resolution)

    # Define the affine transformation for the raster
    transform: Affine = from_bounds(
        bounds[0], bounds[1], bounds[2], bounds[3], width, height
    )
    assert isinstance(transform, Affine)

    # Create empty arrays for RGB and Alpha channels
    r_channel = np.zeros((height, width), dtype=np.uint8)
    g_channel = np.zeros((height, width), dtype=np.uint8)
    b_channel = np.zeros((height, width), dtype=np.uint8)
    alpha_channel = np.zeros((height, width), dtype=np.uint8)

    # Group geometries by color
    grouped = gdf.groupby("color")

    # Rasterize each color group
    for color, group in grouped:
        red, green, blue = color_to_rgb(str(color))
        shapes = (
            (geom.buffer(buffer_width), 1)
            if geom.geom_type == "Point"
            else (geom.boundary.buffer(buffer_width), 1)
            for geom in group.geometry
        )
        mask = rasterize(
            shapes,
            out_shape=(height, width),
            transform=transform,
            fill=0,
            dtype=np.uint8,
        )

        # Apply color and set alpha for geometries
        r_channel[mask == 1] = red
        g_channel[mask == 1] = green
        b_channel[mask == 1] = blue
        alpha_channel[mask == 1] = 255  # Fully opaque for geometries

    # Create an RGBA image using Pillow for adding text
    rgba_image = np.stack([r_channel, g_channel, b_channel, alpha_channel], axis=-1)

    image = Image.fromarray(rgba_image, mode="RGBA")
    image.info["transform"] = transform
    return image


def _add_text_width_column(gdf: GeoDataFrame, font_size: int = 24):
    """
    Add a column to the GeoDataFrame with the width of the text labels.
    """
    font = ImageFont.truetype(FONT_PATH, font_size)
    gdf["text_width"] = gdf["name"].apply(lambda x: font.getlength(str(x)))
    return gdf


# Step 2: Rasterize geometries into a GeoTIFF
def _geodataframe_to_geotiff(
    gdf: GeoDataFrame,
    output_file: Path,
    resolution: float = 0.5,
    outline_width: int = 4,
    font_size: int = 24,
    font_color: str | None = None,
    offset: tuple[int, int] = (0, 0),
):
    gdf = _add_text_width_column(gdf, font_size)
    image = _draw_geomteries(gdf, resolution, outline_width)

    _draw_text_labels(
        image,
        gdf,
        image.info["transform"],
        font_size=font_size,
        color=font_color,
        offset=offset,
    )

    # Write RGB raster to a GeoTIFF
    with rasterio.open(
        output_file,
        "w",
        driver="GTiff",
        height=image.height,
        width=image.width,
        count=4,
        dtype="uint8",
        crs=gdf.crs,
        transform=image.info["transform"],
        compress="deflate",
        tiled=True,
        zlevel=9,
    ) as dst:
        dst.write(np.array(image)[:, :, 0], 1)  # Red channel
        dst.write(np.array(image)[:, :, 1], 2)  # Green channel
        dst.write(np.array(image)[:, :, 2], 3)  # Blue channel
        dst.write(np.array(image)[:, :, 3], 4)  # Alpha channel

        print(f"GeoTIFF saved as {output_file}")


def kml_to_geotiff(
    kml_file: Path,
    output_file: Path,
    resolution: float = 0.5,
    outline_width: int = 4,
    font_size: int = 24,
    font_color: str | None = None,
    offset: tuple[int, int] = (0, 0),
):
    """
    Convert a KML file to a GeoTIFF file with geometries and labels.
    """

    gdf = _parse_kml_to_geodataframe(kml_file)

    _geodataframe_to_geotiff(
        gdf, output_file, resolution, outline_width, font_size, font_color, offset
    )


def placemarks_to_geotiff(
    placemarks: list,
    output_file: Path,
    resolution: float = 0.5,
    outline_width: int = 4,
    font_size: int = 24,
    font_color: str | None = None,
    offset: tuple[int, int] = (0, 0),
):
    """
    Convert a list of KML placemarks to a GeoTIFF file with geometries and labels.
    """

    gdf = _kml_placemarks_to_geodataframe(placemarks)

    _geodataframe_to_geotiff(
        gdf, output_file, resolution, outline_width, font_size, font_color, offset
    )


if __name__ == "__main__":
    kml_file = Path(sys.argv[1])

    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        output_file = kml_file.with_suffix(".tif")

    kml_to_geotiff(kml_file, output_file)
