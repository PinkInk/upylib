# Randomised Prim's algorithm
# https://en.wikipedia.org/wiki/Maze_generation_algorithm

from random import randint


class Maze():

    def __init__(self, width, height):
        assert width%2 and height%2, 'width & height must be odd'
        self.width, self.height = width, height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]
        # Pick a cell, mark it as part of the maze.
        self((0, 0), 0)
        # Add its walls to the walls list
        walls = set(self.adjacent_walls((0, 0)))
        # whilst there are walls
        while walls:
            # pick a random wall from the set
            wall = list(walls)[randint(0, len(walls)-1)]
            # if only one of the cells that the wall divides is visited
            cells = self.adjacent_unvisited_cells(wall)
            if len(cells) == 1:
                cell = cells[0]
                # Make the wall a passage
                self(wall, 0)
                # Mark unvisited cell part of maze
                self(cell, 0)
                # Add the neighboring walls of the cell to the wall list
                walls.update(self.adjacent_walls(cell))
            walls.discard(wall)

    def __call__(self, pt, v=None):
        assert 0 <= pt[0] < self.width and 0 <= pt[1] < self.height, 'out of bounds'
        if v is None:
            return self.maze[pt[1]][pt[0]]
        else:
            self.maze[pt[1]][pt[0]] = v

    def adjacent_unvisited_cells(self, pt):
        v = (1, 0) if pt[0]%2 else (0, 1)
        cells = []
        for cell in self._neighbours(pt, v, 2):
            if self(cell): # unvisited = 1
                cells.append(cell)
        return cells

    def adjacent_walls(self, pt):
        return self._neighbours(pt, (0, 1), 4)

    def _neighbours(self, pt, v, div):
        assert div in (4, 2), 'div must be 2 or 4'
        for _ in range(div):
            if 0 <= pt[0]+v[0] < self.width and 0 <= pt[1]+v[1] < self.height:
                yield pt[0]+v[0], pt[1]+v[1]
            for _ in range(4//div):
                v = -v[1], v[0] # rotate 90d

    def __repr__(self):
        b = chr(128) # renders as a box (PuTTY)
        v = b*(self.width+2) + '\n'
        for y in range(self.height):
            v += b + ''.join([b if i == 1 else ' ' for i in self.maze[y]]) + b + '\n'
        v += b*(self.width+2)
        return v
