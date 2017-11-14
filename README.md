# minesweeper_solver
The minesweeper solver is a tool which can solve Microsoft Minesweeper with the "Modern" design automatically.

All map sizes are supported, but the field has to be big enough in order to recognize all numbers

The map of the game is recognized automatically by scanning the screen. Then the solver analyzes the map and decides which fields can be open and where the mines are. To open a field a mouseclick will be simulated.

Planned improvements:
- optimize map recognition, especially '6' and '7'
- improve solving algorithm with more complex structures
- check if try except is very slow
