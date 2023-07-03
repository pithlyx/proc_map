import colorama
from colorama import Fore, Back, Style
import readchar
import os
import json
from enum import Enum
import random
import string

colorama.init()

class Direction(Enum):
    NORTH = 'n'
    EAST = 'e'
    SOUTH = 's'
    WEST = 'w'

class Tile:
    """Tile in the grid with x, y coordinates and a unique id."""
    def __init__(self, x, y, tile_id,seed, type=None):
        self.x = x
        self.y = y
        self.tile_id = tile_id
        # Use a hash function to generate a consistent value based on coordinates and seed
        self.seed = f'{x},{y},{seed}'
        self.is_occupied = False
        self.can_interact = False
        self.tile_type = None
        self.set_type(type)

    def set_type(self, tile_type):
        types = {
            'empty': [.75, '🞑', Fore.GREEN, False, False],
            'wall': [.2, '◼', Fore.RED, True, False],
            'shrine': [.05, '🞖', Fore.YELLOW, False, True],
        }
        tile_type = tile_type or self.deterministic_tile_type(types)
        if tile_type in types:
            self.tile_type = tile_type
            self.icon, self.color, self.has_collision, self.can_interact = types[tile_type][1:]
        else:
            raise ValueError(f"Invalid tile type: {tile_type}")

    def deterministic_tile_type(self, types):
        """Deterministically assign tile type based on coordinates and seed."""
        random.seed(self.seed)
        # Select the tile type based on the hash value
        return random.choices(list(types.keys()), weights=[w[0] for w in types.values()])[0]

    def interact(self):
        """Interact with the tile."""
        if not self.can_interact:
            raise ValueError(f'{self.tile_id} at ({self.x}, {self.y}) cannot be interacted with')
        if self.tile_type == 'shrine':
            self.can_interact = False
            self.color = Fore.BLACK
            return random.choice(['You feel a strange power ...', 'You feel a strange presence ...', 'You feel a strange energy ...'])

    def __str__(self):
        icon = self.icon
        if self.is_occupied:
            icon = '🞚'
        if self.tile_type == "shrine":
            icon = '🞖' if self.can_interact else '🞔'
            if self.is_occupied:
                icon = '🞛' if self.can_interact else '🞜'
        color = Fore.CYAN if self.is_occupied else self.color
        return color+icon+Style.RESET_ALL

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

    def get_display(self, x, y, radius=None):
        """Print the grid of tiles within a radius from (x, y)."""
        radius = radius or self.viewport
        surrounding_tiles = self.grid.get_radius(x, y, radius)
        print(f"X: {x} | Y: {y} | Tile_ID: {self.current_tile.tile_id} | Tile_Type: {self.current_tile.tile_type}")
        print(f"Bombs: {self.bombs}")
        display = ''
        for row in surrounding_tiles:
            for tile in row:
                display += f'{Fore.BLACK}▨{Style.RESET_ALL} ' if tile is None else f'{tile} '
            display+= '\n'
        return display

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


def menu(cont):
    """Handle user input and game interaction."""
    direction_mapping = {
        Direction.NORTH:['\x1b[A', '^[[A', '\x1bOA', '^[[1~', 'w'],
        Direction.WEST: ['\x1b[D', '^[[D', '\x1bOD', '^[[3~', 'a'],
        Direction.SOUTH: ['\x1b[B', '^[[B', '\x1bOB', '^[[2~', 's'],
        Direction.EAST: ['\x1b[C', '^[[C', '\x1bOC', '^[[4~', 'd']
    }

    hotkeys = {
        'import': ['i'],
        'export': ['o'],
        'reset':['\x7f'], # Backspace
        'bomb': ['q'],
        'gen_down': ['[', '-'],
        'gen_up': [']','='],
        'interact': ['e', ' '],


    }


    for direction in direction_mapping:
        if direction is not None:
            continue
        print(f"Please press the key to map the '{direction.name.capitalize()}' direction")
        key = readchar.readkey()
        direction_mapping[direction] = [key]
    print(direction_mapping)

    while True:
        display = f'{"▬ "*(cont.viewport*2)+"▬"}\n{cont.get_display(cont.x, cont.y)}\n{"▬ "*(cont.viewport*2)+"▬"}'
        print(display)
        key = readchar.readkey()
        direction = next(
            (
                dir_key
                for dir_key, mappings in direction_mapping.items()
                if key in mappings
            ),
            None,
        )
        if key in hotkeys['reset']:  # Reset grid
            new_seed = get_random_string(8)
            cont.__init__(cont.viewport, cont.gen_range, new_seed)
            print(f"Grid reset with the new seed: {new_seed}.")
            continue

        elif key in hotkeys['gen_down']:  # Reduce generation range
            cont.gen_range = max(1, cont.gen_range - 1)
            print(f"Generation range reduced to {cont.gen_range}")
            continue

        elif key in hotkeys['gen_up']:  # Increase generation range
            cont.gen_range += 1
            print(f"Generation range increased to {cont.gen_range}")
            continue

        elif key in hotkeys['export']:  # Export grid
            save_name = input("Enter a name for the save: ")
            if not save_name:
                print("Save cancelled.")
                continue
            cont.save_grid(save_name)
            print(f"Game saved with name '{save_name}'")
            continue

        elif key in hotkeys['import']:  # Import grid
            while True:
                save_name = input("Enter the name of the save to load: ")
                if not save_name:
                    print("Load cancelled.")
                    break
                if not cont.saved:  # Check if the current game has been saved
                    overwrite = input("Do you want to overwrite the current game? (y/n): ")
                    if overwrite.lower() != 'y':
                        print("Load cancelled.")
                        break
                try:
                    cont.load_grid(save_name)
                    print(f"Game loaded from save '{save_name}'")
                    break
                except Exception as e:
                    print(e)
                    break
            continue

        elif key in hotkeys['bomb']: # Toggle bombing
            if cont.bombs > 0:
                cont.is_bombing = not cont.is_bombing
            else:
                print("You don't have any bombs left.")

        elif key in hotkeys['interact']: # Interact with tile
            try:
                if not cont.current_tile.can_interact:
                    continue
                elif cont.current_tile.tile_type == 'shrine':
                    print(cont.current_tile.interact())
                    cont.bombs += 1 if cont.bombs < 5 else 0

            except Exception as e:
                print(e)


        elif direction is None:
            print('Invalid direction')
            continue

        try:
            cont.move(direction)
        except Exception as e:
            print(e)


def get_random_string(length):
    # Define the pool of characters to choose from
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


if __name__ == '__main__':
    seed = input("Enter the global seed: ") or get_random_string(8)
    print(f"Global seed: {seed}")
    gen_range = input("Enter the generation range: ") or 1
    viewport = input("Enter the viewport size: ") or 10
    cont = Controller(int(viewport), int(gen_range), seed)
    while True:
        print("1. Play")
        opt = input("Enter your option: ") or '1'
        if opt == '1':
            menu(cont)
        else:
            print("Invalid option.")
