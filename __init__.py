from lib.types import TileDistance, TileInfo, MAX_HEIGHT, MAX_WIDTH
from lib.utils import compute_weight
from lib.map import TileMap
import sys
from typing import Sequence

def _land(x, y) -> TileInfo:
    return TileInfo(
                x=x,
                y=y,
                alt=0,
                fertility=60,
                forest=None,
                res=None,
                res_amount=None,
                region=None,
                area=None,
                type=None,
            )

def _sea(x, y) -> TileInfo:
    return TileInfo(
                x=x,
                y=y,
                alt=0,
                fertility=60,
                forest=None,
                res=None,
                res_amount=None,
                region=None,
                area=None,
                type=1,
            )

map = [
    _land(0, 0), _land(0, 1), _land(0, 2),
    _land(1, 0), _sea(1, 1),  _land(1, 2),
    _land(2, 0), _land(2, 1), _land(2, 2),
]


def _generate_tiles(height: int, width: int) -> Sequence[TileInfo]:
    tiles = []
    for i in range(height):
        for j in range(width):
            tiles.append(TileInfo(
                x=i,
                y=j,
                alt=0,
                fertility=60,
                forest=None,
                res=None,
                res_amount=None,
                region=None,
                area=None,
                type=None,
            ))
    return tiles

def print_tiles(tiles: Sequence[TileInfo]) -> None:
    for t in tiles:
        print(f'x={t.x} y={t.y} key={t.key}')

tiles = map
map = TileMap(tiles)
map.compute_costs()
dist_arr = map.compute_distances(0, 0)

def convert_to_matrix(dist: Sequence[TileDistance]) -> list[list[int | None]]:
    matrix = [[None for _ in range(MAX_WIDTH)] for _ in range(MAX_HEIGHT)]
    for d in dist:
        matrix[d.x][d.y] = d.distance
    return matrix

for row in convert_to_matrix(dist_arr):
    print(row)

print(convert_to_matrix(dist_arr)[1][1] == sys.float_info.max)
