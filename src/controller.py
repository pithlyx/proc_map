from src.grid import Grid
from src.direction import Direction
from colorama import Fore, Style
import json


class Controller:
    """Game controller handling game logic and user interaction."""
    def __init__(self, viewport, gen_range, seed):
        self.viewport = viewport
        self.gen_range = gen_range
        self.grid = Grid(seed)
        self.x = 0
        self.y = 0
        self.current_tile = self.grid.get_tile(self.x, self.y)
        self.enter_current_tile()
        self.saved = True
        self.max_bombs = 5
        self.bombs = 3
        self.is_bombing = False


    def move(self, direction):
        """Move to the tile in the given direction."""
        dx, dy = {
            Direction.NORTH: (-1, 0),
            Direction.EAST: (0, 1),
            Direction.SOUTH: (1, 0),
            Direction.WEST: (0, -1)
        }[direction]
        next_x, next_y = self.x + dx, self.y + dy
        next_tile = self.grid.get_tile(next_x, next_y)
        if next_tile is None or next_tile not in self.available_tiles:
            raise ValueError('Cannot move in that direction')
        if next_tile.has_collision:
            if not self.is_bombing:
                raise ValueError('Cannot move into a tile with collision')
            self.bombs -= 1
            next_tile.has_collision = False
            next_tile.icon = '🞑'
            next_tile.color = Fore.LIGHTGREEN_EX
        self.leave_current_tile(next_tile)
        self.enter_current_tile()
        self.is_bombing = False
        self.saved = False

    def enter_current_tile(self):
        """Enter the current tile and update available tiles."""
        self.current_tile.is_occupied = True
        self.available_tiles = self.grid.generate_tiles_in_range(self.x, self.y, self.gen_range)

    def leave_current_tile(self, next_tile):
        """Leave the current tile and move to the next tile."""
        self.current_tile.is_occupied = False
        self.current_tile = next_tile
        self.x = self.current_tile.x
        self.y = self.current_tile.y

    def display_grid(self, x, y, radius=None):
        """Print the grid of tiles within a radius from (x, y)."""
        radius = radius or self.viewport
        surrounding_tiles = self.grid.get_radius(x, y, radius)
        print(f"X: {x} | Y: {y} | Tile_ID: {self.current_tile.tile_id} | Tile_Type: {self.current_tile.tile_type}")
        print(f"Bombs: {self.bombs}")
        for row in surrounding_tiles:
            for tile in row:
                if tile is None:
                    print(f'{Fore.BLACK}▨{Style.RESET_ALL}', end=' ')
                else:
                    print(f'{tile}', end=' ')
            print()

    def grid_to_string(self):
        """Converts the grid to a string representation."""
        grid_string = f"{self.grid.seed}|"
        for key, tile in self.grid.grid.items():
            tile_string = f"[{tile.x},{tile.y},{tile.tile_id},{tile.tile_type},{tile.can_interact}"
            if tile.is_occupied:
                tile_string += ",occupied"
            tile_string += "]"
            grid_string += tile_string
        return grid_string

    def string_to_grid(self, grid_string):
        """Converts a string representation of the grid back into a grid of tiles."""
        seed, grid_string = grid_string.split('|', 1)
        self.grid.seed = seed
        grid = {}
        for tile_string in grid_string.split(']['):
            tile_string = tile_string.replace('[', '').replace(']', '')
            tile_values = tile_string.split(',')
            x, y, tile_id = map(int, tile_values[:3])
            tile_type = tile_values[3]
            can_interact = tile_values[4] == 'True'
            is_occupied = len(tile_values) > 5 and tile_values[5] == "occupied"
            tile = Tile(x, y, tile_id, self.grid.seed, type=tile_type)
            tile.can_interact = can_interact
            tile.is_occupied = is_occupied
            grid[(x, y)] = tile
        return grid

    def save_grid(self, save_name, filename="saves.json"):
        """Saves the current state of the grid to a file."""
        grid_string = self.grid_to_string()
        try:
            with open(filename, 'r') as f:
                saves = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            saves = {}
        if save_name in saves:
            overwrite = input(f"A save with the name '{save_name}' already exists. Do you want to overwrite it? (y/n): ")
            if overwrite.lower() != 'y':
                i = 1
                while f"{save_name}_{i}" in saves:
                    i += 1
                save_name = f"{save_name}_{i}"
        saves[save_name] = grid_string
        with open(filename, 'w') as f:
            json.dump(saves, f)
        self.saved = True
        print(f"Map has been saved as '{save_name}'")

    def load_grid(self, save_name, filename="saves.json"):
        """Loads a saved state of the grid from a file."""
        with open(filename, 'r') as f:
            saves = json.load(f)
        grid_string = saves.get(save_name)
        if grid_string is None:
            raise ValueError(f"No save found with name {save_name}")
        self.grid.grid = self.string_to_grid(grid_string)
        for tile in self.grid.grid.values():
            if tile.is_occupied:
                self.x = tile.x
                self.y = tile.y
                self.current_tile = tile
                break
        self.enter_current_tile()
        self.saved = True