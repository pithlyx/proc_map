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

class DynamicGrid:
    """Grid of nodes with dynamic generation."""
    def __init__(self, seed):
        self.grid = {}
        self.node_count = 0
        self.seed = seed
        self.create_node(0, 0, type = 'empty')

    def get_node(self, x, y):
        return self.grid.get((x, y))

    def create_node(self, x, y, type = None):
        self.node_count += 1
        node = Node(x, y, self.node_count, self.seed, type = type)
        self.grid[(x, y)] = node
        return node

    def get_radius(self, x, y, radius):
        """Get nodes within a radius from (x, y)."""
        return [[self.get_node(x + i, y + j) for j in range(-radius, radius + 1)] for i in range(-radius, radius + 1)]

    def generate_nodes_in_range(self, x, y, range):
        """Generate nodes within a range from (x, y)."""
        queue = [(x, y, 0)]
        visited = {(x, y)}
        nodes_in_range = []

        while queue:
            current_x, current_y, depth = queue.pop(0)
            if depth > range:
                break
            node = self.get_node(current_x, current_y) or self.create_node(current_x, current_y)
            nodes_in_range.append(node)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                next_x, next_y = current_x + dx, current_y + dy
                if (next_x, next_y) not in visited:
                    queue.append((next_x, next_y, depth + 1))
                    visited.add((next_x, next_y))

        return nodes_in_range

class Controller:
    """Game controller handling game logic and user interaction."""
    def __init__(self, viewport, gen_range, seed):
        self.viewport = viewport
        self.gen_range = gen_range
        self.grid = DynamicGrid(seed)
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
        cont.display_grid(cont.x, cont.y)
        print(f'Current node: {cont.current_node.node_id}')

        key = readchar.readkey()
        direction = None
        for dir_key, mappings in direction_mapping.items():
            if key in mappings:
                direction = dir_key
                break

        if key in hotkeys['reset']:  # Reset grid
            cont.__init__(cont.viewport, cont.gen_range, cont.grid.seed)
            print("Grid reset to initial state.")
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

        elif key in hotkeys['interact']: # Interact with node
            if not cont.current_node.can_interact:
                continue
            elif cont.current_node.node_type == 'shrine':
                print(cont.current_node.interact())
                bomb_count = random.randint(1, 3)
                cont.bombs += bomb_count


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
    # Generate a random string of the specified length
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


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
