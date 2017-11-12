# minesweeper_solver
The minesweeper solver is a tool which can solve Microsoft Minesweeper with the "Modern" design automatically.

The map of the game is recognized automatically by scanning the screen. Then the solver analyzes the map and decides which fields can be open and where the mines are. To open a field a mouseclick will be simulated.

Planned improvements:
- add solving algorithm
- stop script when all bombs are found
- if it's not possible to find a field to open with logic, the solver should open a field randomly
- optimize map recognition