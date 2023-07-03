from colorama import Fore, Style
import random

class Node:
    """Node in the grid with x, y coordinates and a unique id."""
    def __init__(self, x, y, node_id,seed, type=None):
        self.x = x
        self.y = y
        self.node_id = node_id
        # Use a hash function to generate a consistent value based on coordinates and seed
        self.seed = f'{x},{y},{seed}'
        self.is_occupied = False
        self.can_interact = False
        self.node_type = None
        self.set_type(type)

    def set_type(self, node_type):
        types = {
            'empty': [.75, '▢', Fore.GREEN, False, False],
            'wall': [.2, '◼', Fore.RED, True, False],
            'shrine': [.05, '◉', Fore.YELLOW, False, True],
        }
        node_type = node_type or self.deterministic_node_type(types)
        self.node_type = node_type
        if node_type in types:
            self.icon, self.color, self.has_collision, self.can_interact = types[node_type][1:]
        else:
            raise ValueError(f"Invalid node type: {node_type}")

    def deterministic_node_type(self, types):
        """Deterministically assign node type based on coordinates and seed."""
        random.seed(self.seed)
        # Select the node type based on the hash value
        return random.choices(list(types.keys()), weights=[w[0] for w in types.values()])[0]

    def interact(self):
        """Interact with the node."""
        if self.node_type == 'shrine':
            self.set_type('empty')
            return random.choice(['You feel a strange power ...', 'You feel a strange presence ...', 'You feel a strange energy ...'])

    def __str__(self):
        icon = self.icon if not self.is_occupied else '◇' if not self.can_interact else '◈'
        color = self.color if not self.is_occupied else Fore.CYAN
        return color+icon+Style.RESET_ALL
