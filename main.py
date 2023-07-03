import colorama
import readchar
import random
from src.controller import Controller
from src.direction import Direction
from src.utils import get_random_string


colorama.init()


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