from rasterio.control import GroundControlPoint


def get_gcps(
    corner_coords: list[tuple[float, ...]],
    image_width: int,
    image_height: int,
) -> list[GroundControlPoint]:
    """
    Create Ground Control Points (GCPs) for georeferencing an image.

    Args:
        corner_coords (list[tuple[float, float]]): Geographic coordinates of the image corners.
        image_width (int): Image width in pixels.
        image_height (int): Image height in pixels.

    Returns:
        list[GroundControlPoint]: A list of GCPs mapping image corners to geographic
    """

    # Define image coordinates for the corners (row, col) starting from top-left
    image_coords = [
        (0, 0),  # Upper-left (UL)
        (0, image_width - 1),  # Upper-right (UR)
        (image_height - 1, image_width - 1),  # Lower-right (LR)
        (image_height - 1, 0),  # Lower-left (LL)
    ]

    # Create GCPs (Ground Control Points) mapping image corners to geographic coordinates
    return [
        GroundControlPoint(
            row=image_coords[i][0],
            col=image_coords[i][1],
            x=corner_coords[i][0],  # Longitude
            y=corner_coords[i][1],  # Latitude
            z=0,  # Elevation (optional, usually 0 for 2D)
        )
        for i in range(4)
    ]
