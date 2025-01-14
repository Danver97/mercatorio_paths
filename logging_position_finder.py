from lib.types import TileDistance, TileWeight
import os.path
from typing import Sequence, Iterable, Tuple
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

def circle_boundaries(radius) -> Sequence[Tuple[int, int, int]]:
    # Radius needs to be an integer for this grid-based approach
    radius = radius - 1 # excluding the center
    boundaries = []
    
    # Determine the size of the grid
    for x in range(-radius, radius + 1):
        line_boundaries = []
        for y in range(-radius, radius + 1):
            # Equation of a circle: x^2 + y^2 = r^2
            distance = (x**2 + y**2)**0.5
            # if radius - 0.5 <= distance <= radius:
            if radius - 0.5 <= distance <= radius + 0.5:
                line_boundaries.append(y)
                # print("#", end="")
            else:
                # print(" ", end="")
                pass
        boundaries.append((x, min(line_boundaries), max(line_boundaries)))
        # print()
    return boundaries

def compute_ranges(coords: Tuple[int, int], radius: int) -> Sequence[Tuple[Tuple[int, int], Tuple[int, int]]]:
    x, y = coords
    boundaries = circle_boundaries(radius)
    ranges = []
    for b in boundaries:
        (offset_x, offset_y_left, offset_y_right) = b
        ranges.append(((x + offset_x, y + offset_y_left), (x + offset_x, y + offset_y_right)))
    return ranges

def is_in_range(target: tuple[int, int], t: TileWeight, radius: int = 8) -> bool:
    # ranges = [
    #     [(target_x + 7, target_y - 2), (target_x + 7, target_y + 2)],
    #     [(target_x + 6, target_y - 4), (target_x + 6, target_y + 4)],
    #     [(target_x + 5, target_y - 5), (target_x + 5, target_y + 5)],
    #     [(target_x + 4, target_y - 6), (target_x + 4, target_y + 6)],
    #     [(target_x + 3, target_y - 6), (target_x + 3, target_y + 6)],
    #     [(target_x + 2, target_y - 7), (target_x + 2, target_y + 7)],
    #     [(target_x + 1, target_y - 7), (target_x + 1, target_y + 7)],

    #     [(target_x + 0, target_y - 7), (target_x + 0, target_y + 7)],

    #     [(target_x - 1, target_y - 7), (target_x - 1, target_y + 7)],
    #     [(target_x - 2, target_y - 7), (target_x - 2, target_y + 7)],
    #     [(target_x - 3, target_y - 6), (target_x - 3, target_y + 6)],
    #     [(target_x - 4, target_y - 6), (target_x - 4, target_y + 6)],
    #     [(target_x - 5, target_y - 5), (target_x - 5, target_y + 5)],
    #     [(target_x - 6, target_y - 4), (target_x - 6, target_y + 4)],
    #     [(target_x - 7, target_y - 2), (target_x - 7, target_y + 2)],
    # ]
    ranges = compute_ranges(target, radius)

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

c_x, c_y = (2090, 3150)
size = 46
min_x, max_x, min_y, max_y = (c_x - size / 2, c_x + size / 2, c_y - size / 2, c_y + size / 2)

tiles_map = load_map(MAP_DIR)

existing_camp_1 = (2105, 3131)
existing_camp_2 = (2104, 3142)
# existing_camp_3 = (2093, 3152) Soon to be

def _print(target: tuple[int, int], tiles: Sequence[Sequence[TileWeight]], outpost: tuple[int, int] = None):
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
            if outpost is not None and t.x == outpost[0] and t.y == outpost[1]:
                str_to_print += '@'
                continue
            if (t.forest is not None):
                if is_in_range(existing_camp_1, t) or is_in_range(existing_camp_2, t):
                    str_to_print += '#'
                elif is_in_range(target, t):
                    str_to_print += 'O'
                elif t.x >= 2097: # limit for claimable tiles
                    str_to_print += 'X'
                else:
                    if outpost is not None and is_in_range(outpost, t, radius=30):
                        str_to_print += '+'
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

outpost = (2099, 3155)  # +2, +5
targets = [(2090, 3150), (2093, 3152)]

def count_forest_tiles(targets: Sequence[tuple[int, int]]) -> Sequence[tuple[tuple[int, int], int]]:
    results = []
    for target in targets:
        c = 0
        for t_row in tiles_of_interest:
            for t in t_row:
                if is_in_range(target, t) and t.forest is not None and not (is_in_range(existing_camp_1, t) or is_in_range(existing_camp_2, t)):
                    c += 1
        results.append((target, c))
    return results

# Possible outposts
# 2099, 3150
# 2097, 3150
print(count_forest_tiles(targets))

# (2105, 3135) ok, but on the bottom limit for x for claiming territories. Maybe moving it to the "left" (i.e. lower y)

_print((2090, 3150), tiles_of_interest, outpost=outpost)
_print((2093, 3152), tiles_of_interest, outpost=outpost)
