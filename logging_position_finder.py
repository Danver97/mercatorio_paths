from lib.types import TileDistance, TileWeight
import os.path
from typing import Sequence, Iterable
from utils import decompress, load_map


#    ^
#  x |   y -->
#
#     -7-6  -4  -2   0  +2  +4  +6+7
#                              
# +7             o o o o o
# +6         o o     ^     o o
#          o         |         o
# +4     o           |           o
#        o     5     7     5     o
# +2   o             |             o
#      o             |             o
#  0   o<-----7------x------7----->o       
#      o             |             o
# -2   o             |             o
#        o     5     7     5     o
# -4     o           |           o
#          o         |         o
# -6         o o     v     o o
# -7             o o o o o
def is_in_range(target: tuple[int, int], t: TileWeight) -> bool:
    target_x, target_y = target

    ranges = [
        [(target_x + 7, target_y - 2), (target_x + 7, target_y + 2)],
        [(target_x + 6, target_y - 4), (target_x + 6, target_y + 4)],
        [(target_x + 5, target_y - 5), (target_x + 5, target_y + 5)],
        [(target_x + 4, target_y - 6), (target_x + 4, target_y + 6)],
        [(target_x + 3, target_y - 6), (target_x + 3, target_y + 6)],
        [(target_x + 2, target_y - 7), (target_x + 2, target_y + 7)],
        [(target_x + 1, target_y - 7), (target_x + 1, target_y + 7)],

        [(target_x + 0, target_y - 7), (target_x + 0, target_y + 7)],

        [(target_x - 1, target_y - 7), (target_x - 1, target_y + 7)],
        [(target_x - 2, target_y - 7), (target_x - 2, target_y + 7)],
        [(target_x - 3, target_y - 6), (target_x - 3, target_y + 6)],
        [(target_x - 4, target_y - 6), (target_x - 4, target_y + 6)],
        [(target_x - 5, target_y - 5), (target_x - 5, target_y + 5)],
        [(target_x - 6, target_y - 4), (target_x - 6, target_y + 4)],
        [(target_x - 7, target_y - 2), (target_x - 7, target_y + 2)],
    ]

    # print(target)
    # print((t.x, t.y))
    # print(ranges)

    def _in_interval(left_interval: tuple[int, int], right_interval: tuple[int, int]) -> bool:
        return t.x == left_interval[0] and t.x == right_interval[0] and left_interval[1] <= t.y <= right_interval[1]

    in_range = False
    for r in ranges:
        r_left, r_right = r
        in_range = in_range or _in_interval(r_left, r_right)

    # print(in_range)
    return in_range

# MAP_ARCHIVE = 'map_compressed.gz' # Currently missing some tiles for some reason.
MAP_ARCHIVE = 'compressed.zip'
MAP_DIR = 'map'

# If MAP_DIR doesn't exists yet or is still empty
if not os.path.isdir(MAP_DIR) or not os.listdir(MAP_DIR):
    decompress(MAP_ARCHIVE, MAP_DIR)

c_x, c_y = (2108, 3135)
size = 40
min_x, max_x, min_y, max_y = (c_x - size / 2, c_x + size / 2, c_y - size / 2, c_y + size / 2)

tiles_map = load_map(MAP_DIR)

def _print(target: tuple[int, int], tiles: Sequence[Sequence[TileWeight]]):
    target_x, target_y = target
    # tiles.sort(key=lambda t_row: -t_row[0].x)
    print(f'target: {target_x}, {target_y}')
    print(f'y: {tiles[0][0].y} --> {tiles[0][len(tiles[0])-1].y}')
    for t_row in tiles:
        x_coord = t_row[0].x
        str_to_print = f'{x_coord}: '
        for t in t_row:
            assert t.x == x_coord
            if (t.x == target_x and t.y == target_y):
                if (t.forest is not None):
                    str_to_print += ':'
                else:
                    str_to_print += '.'
                continue
            if (t.forest is not None):
                if is_in_range(target, t):
                    str_to_print += 'O'
                elif t.x >= 2097: # limit for claimable tiles
                    str_to_print += 'X'
                else:
                    str_to_print += '-'
            else:
                str_to_print += ' '
        print(str_to_print)

# Group by rows
def to_matrix(tiles: Iterable[TileWeight]) -> Sequence[Sequence[TileWeight]]:
    tiles_of_interest_dict = {}

    for t in tiles:
        if t.x not in tiles_of_interest_dict:
            tiles_of_interest_dict[t.x] = []
        tiles_of_interest_dict[t.x].append(t)

    for k in tiles_of_interest_dict.keys():
        tiles_of_interest_dict[k].sort(key=lambda t: t.y)
    
    matrix = list(tiles_of_interest_dict.values())
    matrix.sort(key=lambda t_row: -t_row[0].x)
    return matrix

tiles_of_interest = to_matrix(filter(lambda t: min_x < t.x < max_x and min_y < t.y < max_y, tiles_map))

# _print(tiles_of_interest)

targets = [(2104, 3135), (2105, 3135), (2107, 3135), (2109, 3135), (2109, 3131), (2105, 3131)]

def count_forest_tiles(targets: Sequence[tuple[int, int]]) -> Sequence[tuple[tuple[int, int], int]]:
    results = []
    for target in targets:
        c = 0
        for t_row in tiles_of_interest:
            for t in t_row:
                if is_in_range(target, t) and t.forest is not None:
                    c += 1
        results.append((target, c))
    return results

print(count_forest_tiles(targets))

# (2105, 3135) ok, but on the bottom limit for x for claiming territories. Maybe moving it to the "left" (i.e. lower y)

_print((2105, 3135), tiles_of_interest)
_print((2109, 3131), tiles_of_interest)
_print((2105, 3131), tiles_of_interest)
