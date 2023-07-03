class Grid:
    """Grid of tiles with dynamic generation."""
    def __init__(self, seed):
        self.grid = {}
        self.tile_count = 0
        self.seed = seed
        self.create_tile(0, 0, type = 'empty')

    def get_tile(self, x, y):
        return self.grid.get((x, y))

    def create_tile(self, x, y, type = None):
        from src.tile import Tile
        self.tile_count += 1
        tile = Tile(x, y, self.tile_count, self.seed, type = type)
        self.grid[(x, y)] = tile
        return tile

    def get_radius(self, x, y, radius):
        """Get tiles within a radius from (x, y)."""
        return [[self.get_tile(x + i, y + j) for j in range(-radius, radius + 1)] for i in range(-radius, radius + 1)]

    def generate_tiles_in_range(self, x, y, range):
        """Generate tiles within a range from (x, y)."""
        queue = [(x, y, 0)]
        visited = {(x, y)}
        tiles_in_range = []

        while queue:
            current_x, current_y, depth = queue.pop(0)
            if depth > range:
                break
            tile = self.get_tile(current_x, current_y) or self.create_tile(current_x, current_y)
            tiles_in_range.append(tile)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                next_x, next_y = current_x + dx, current_y + dy
                if (next_x, next_y) not in visited:
                    queue.append((next_x, next_y, depth + 1))
                    visited.add((next_x, next_y))

        return tiles_in_range
