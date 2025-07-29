from typing import Generator


def get_tiles(
    layers_bounds: list[tuple[int, int, int, int]],
) -> Generator[tuple[int, int, int], None, None]:
    def process_tile(
        layer: int, x: int, y: int
    ) -> Generator[tuple[int, int, int], None, None]:
        if layer < 0 or layer >= len(layers_bounds):
            return

        layer_bounds = layers_bounds[layer]

        if x >= layer_bounds[2] or y >= layer_bounds[3]:
            return

        if x < layer_bounds[0] or y < layer_bounds[1]:
            return

        for dy in range(2):
            for dx in range(2):
                yield from process_tile(layer + 1, x * 2 + dx, y * 2 + dy)

        yield (layer, x, y)

    for y in range(layers_bounds[0][3]):
        for x in range(layers_bounds[0][2]):
            yield from process_tile(0, x, y)
