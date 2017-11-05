# minesweeper_solver
The minesweeper solver is a tool which can solve Microsoft Minesweeper automatically.

The map of the game is recognized automatically by scanning the screen. Then the solver analyzes the map and decides which fields can be open. To open a field a mouseclick will be simulated.

Planned improvements:
- fix bug with path to files (not absolut)
- add solving algorithm
- easy change for different size of map
- scan screen automatically for map
- improve performance by scanning map just once and extract infos from this scan
- stop script when all bombs are found
- if it's not possible to find a field to open with logic, the solver should open a field randomly
- if a 9 field touches a 0 field (which is not possible) change the parameter of the scanning
- optimize recognition of the numbers (color?)
