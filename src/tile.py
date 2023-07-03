import random
from colorama import Fore, Style

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
