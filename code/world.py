from tile import *
from collections import defaultdict
from entity import *
import math
from queue import PriorityQueue
from random import random

PIXELS_PER_UNIT = 70

class World:
    def __init__(self):

        self.entities = []

        self.screen_width = [0, 0]

        self.unit_origin = [0, 0]

        self.entities.append(make_player([2, 2]))
        self.entities.append(make_swede([3, 2]))
        self.entities.append(make_flag_am([5, 1.25]))
        self.entities.append(make_flag_sw([7, 1.25]))
        self.entities.append(make_flag_ru([3, 1.25]))
        self.entities.append(make_crucible([3, 3.25]))

        self.tiles = defaultdict(lambda: VOID()) # {(x, y): Tile}
        self.make_cellar(0, 0, "R")
        self.make_cellar(8, 2, "A")
        self.replace_area(8, 8, 3, 4, WALL_PAPER())

        self.tile_nationality = {} # {pos: (nationality, distance to flag)}

        self.update_tile_nationality((2, 2), 'rus')
        print(self.tile_nationality)

    def draw(self, screen):
        self.screen_width = [screen.get_width(), screen.get_height()]

        self.unit_origin = self.entities[0].pos

        for (x, y), tile in self.tiles.items():
            tile.draw(screen, self, (x, y))

        for entity in self.entities:
            entity.draw(self, screen)

    def get_at(self, at):
        at = (int(math.floor(at[0])), int(math.floor(at[1])))
        if at in self.tiles:
            return self.tiles[at], at
        return VOID(), at

    def get_player_idx(self):
        for i in range(len(self.entities)):
            if isinstance(self.entities[i], Russian):
                return i

    def make_cellar(self, xmin, ymin, nationality):
        if nationality == "S":
            xmax = xmin + 10
            ymax = ymin + 7
        elif nationality == "A":
            xmax = xmin + 7
            ymax = ymin + 5
            self.entities.append(make_american([xmin + 3, ymin + 4]))
            self.entities.append(make_american([xmin +5, ymin + 3]))


        else:
            xmax = xmin + 8
            ymax = ymin + 7
        for x in range(xmin, xmax+1):
            for y in range(ymin, ymax+1):
                here = None

                if x == xmin or x == xmax or y == ymin or y == ymax:
                    if self.tiles[(x, y)] == VOID():
                        here = WALL_COBBLE()
                elif self.tiles[(x, y)] == VOID():
                    here = FLOOR_WOOD()
                if here != None:
                    self.tiles[(x, y)] = here

    def onBreakWall(self, tile_x, tile_y):
        rock = make_rock([0, 0])
        rock.pos[0] = tile_x + rock.width / 2 + random() * (1 - rock.width)
        rock.pos[1] = tile_y + rock.height / 2 + random() * (1 - rock.height)

        self.entities.append(rock)

        for x in range(tile_x-1, tile_x+2):
            for y in range(tile_y-1, tile_y+2):
                if self.tiles[(x, y)] == VOID():
                    self.tiles[(x, y)] = WALL_COBBLE()

    def replace_area(self, xmin, xmax, ymin, ymax, newTile):
        for x in range(xmin, xmax+1):
            for y in range(ymin, ymax+1):
                self.tiles[(x, y)] = newTile.copy()

    def transform_position(self, position):
        return [(position[0] - self.unit_origin[0]) * PIXELS_PER_UNIT + self.screen_width[0] / 2, (position[1] - self.unit_origin[1]) * PIXELS_PER_UNIT + self.screen_width[1] / 2]

    def update(self, dt):
        for entity in self.entities:
            entity.update(self, dt)

        for (at, tile) in self.tiles.items():
            tile.update(self, at, dt)

    def update_tile_nationality(self, pos, nationality):
        visited = set()
        visiting = PriorityQueue() # Contains (-distance, (x, y))
        visiting.put((0, pos))

        while not visiting.empty():
            ndist, (x, y) = visiting.get()
            distance = -ndist
            if (x, y) in visited:
                continue

            visited.add((x, y))

            tile, _ = self.get_at((x, y))
            if not isinstance(tile, FloorTile):
                continue

            if (x, y) in self.tile_nationality:
                _, prev_distance = self.tile_nationality[(x, y)]
                if prev_distance <= distance:
                    continue

            self.tile_nationality[(x, y)] = (nationality, distance)
            for dx, dy in [(0, 1), (-1, 0), (0, -1), (1, 0)]:
                rx, ry = x + dx, y + dy
                visit = (-(distance + 1), (rx, ry))
                visiting.put(visit)

    def remove_entity(self, entity):
        self.entities.remove(entity)
