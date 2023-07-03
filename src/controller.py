import json
from colorama import Fore, Style
from src.direction import Direction
from src.grid import Grid
from src.node import Node

class Controller:
    """Game controller handling game logic and user interaction."""
    def __init__(self, viewport, gen_range, seed):
        self.viewport = viewport
        self.gen_range = gen_range
        self.grid = Grid(seed)
        self.x = 0
        self.y = 0
        self.current_node = self.grid.get_node(self.x, self.y)
        self.enter_current_node()
        self.saved = True
        self.bombs = 3
        self.is_bombing = False


    def move(self, direction):
        """Move to the node in the given direction."""
        dx, dy = {
            Direction.NORTH: (-1, 0),
            Direction.EAST: (0, 1),
            Direction.SOUTH: (1, 0),
            Direction.WEST: (0, -1)
        }[direction]
        next_x, next_y = self.x + dx, self.y + dy
        next_node = self.grid.get_node(next_x, next_y)
        if next_node is None or next_node not in self.available_nodes:
            raise Exception('Cannot move in that direction')
        if next_node.has_collision:
            if self.is_bombing:
                self.bombs -= 1
                next_node.has_collision = False
                next_node.icon = '▢'
                next_node.color = Fore.MAGENTA
            else:
                raise Exception('Cannot move into a node with collision')
        self.leave_current_node(next_node)
        self.enter_current_node()
        self.is_bombing = False
        self.saved = False

    def enter_current_node(self):
        """Enter the current node and update available nodes."""
        self.current_node.is_occupied = True
        self.available_nodes = self.grid.generate_nodes_in_range(self.x, self.y, self.gen_range)

    def leave_current_node(self, next_node):
        """Leave the current node and move to the next node."""
        self.current_node.is_occupied = False
        self.current_node = next_node
        self.x = self.current_node.x
        self.y = self.current_node.y

    def display_grid(self, x, y, radius=None):
        """Print the grid of nodes within a radius from (x, y)."""
        radius = radius or self.viewport
        surrounding_nodes = self.grid.get_radius(x, y, radius)
        for row in surrounding_nodes:
            for node in row:
                if node is None:
                    print(Fore.BLACK + '▨' + Style.RESET_ALL, end=' ')
                else:
                    print(f'{node}', end=' ')
            print()

    def grid_to_string(self):
        """Converts the grid to a string representation."""
        grid_string = ""
        for key, node in self.grid.grid.items():
            node_string = f"[{node.x},{node.y},{node.node_id}"
            if node.is_occupied:
                node_string += ",occupied"
            node_string += "]"
            grid_string += node_string
        return grid_string

    def string_to_grid(self, grid_string):
        """Converts a string representation of the grid back into a grid of nodes."""
        grid = {}
        for node_string in grid_string.split(']['):
            node_string = node_string.replace('[', '').replace(']', '')
            node_values = node_string.split(',')
            x, y, node_id = map(int, node_values[:3])
            is_occupied = len(node_values) > 3 and node_values[3] == "occupied"
            node = Node(x, y, node_id)
            node.is_occupied = is_occupied
            grid[(x, y)] = node
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
        for node in self.grid.grid.values():
            if node.is_occupied:
                self.x = node.x
                self.y = node.y
                self.current_node = node
                break
        self.enter_current_node()
        self.saved = True
