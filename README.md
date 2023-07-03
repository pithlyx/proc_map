# Stygian Depths

Stygian Depths is a text-based game where the player navigates a grid of tiles and interacts with different types of tiles. The game provides a controller that handles the game logic and user interaction.

## Features

- Movement: The player can move in four directions (north, east, south, west) within the grid.
- Node Types: Nodes in the grid can have different types, such as empty, wall, and shrine.
- Interaction: The player can interact with certain types of tiles, such as shrines, which provide special effects.
- Generation Range: The game allows the player to adjust the range for generating tiles around the player's current position.
- Saving and Loading: The game provides the ability to save and load the game state.
- Bombing: The player can toggle the bombing mode, which allows them to destroy walls by using bombs.
- Random Seed: The game utilizes a random seed to generate consistent node types based on the player's coordinates.

## How to Play

1. Upon starting the game, you will be prompted to enter the global seed, generation range, and viewport size. You can press Enter to use the default values.
2. Use the arrow keys (or configured keys) to navigate the grid.
3. Interact with tiles by pressing the 'E' key or the spacebar if the current node allows interaction.
4. Press the 'Q' key to equip a bomb. You can destroy walls by moving into them whith a bomb equipped. Ff you move after equipping a bomb and dont use it then it will be unequipped.
5. Press the '[' key to reduce the generation range and ']' key to increase it.
6. Press the 'O' key to export the current game state and save it with a name.
7. Press the 'I' key to import a previously saved game state.
8. To reset the grid to its initial state, press the Backspace key.
9. Enjoy exploring the grid, interacting with tiles, and experimenting with different game options.

## Tile Key

The following table lists the tile types and their symbols used in Stygian Depths:

|      Type      | Default | Can Interact |
| :------------: | :-----: | :----------: |
| Does Not Exist |   `▨`   |   `False`    |
|     Empty      |   `🞑`   |   `False`    |
|      Wall      |   `◼`   |   `False`    |
|     Shrine     |   `🞔`   |     `🞖`      |
|      User      |   `🞚`   |     `🞛`      |



## Hotkeys

The following table lists the hotkeys used in Stygian Depths:

|          Action           |      Hotkey      |
| :-----------------------: | :--------------: |
|     Movement (North)      |    `W` / `Up`    |
|      Movement (West)      |   `A` / `Left`   |
|     Movement (South)      |   `S` / `Down`   |
|      Movement (East)      |  `D` / `Right`   |
|         Interact          | `E` / `Spacebar` |
|        Equip Bomb         |       `Q`        |
| Decrease Generation Range |       `[`        |
| Increase Generation Range |       `]`        |
|         Save Game         |       `O`        |
|         Load Game         |       `I`        |
|        Reset Grid         |   `Backspace`    |

Players can customize the hotkeys for movement and configure their preferred keys during the initial game setup. The game prompts players to enter their desired keys for each movement direction.

These hotkeys provide an intuitive way for players to navigate the grid, interact with nodes, adjust game settings, and perform various actions during gameplay.
