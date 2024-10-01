from __future__ import annotations
from lib.types import Tile, TileInfo
from typing import Sequence

def compute_weight(src: TileInfo, dest: TileInfo, neighbors: Sequence[TileInfo] = (), is_source_town: bool = False) -> float | None:
    # Land movement cost: The cost of one move is l * c + p where 
    # - c is cost of passing through forest (1 for no forest, 1.5 if one plot has forest and 2 if both origin and destination has)
    # - p is altitude penalty (0 for altitude difference <25m, 2 for <75m, 5 for <125m and 20 >= 125m
    # - l (length) is 1 for straight moves and 1.414 for diagonal ones.
    # Sea movement cost: l, where l is 1 for straigh move and 1.414 for diagonals
    assert(src.is_adjacent(dest))

    if is_source_town and not is_crossable_if_source_is_town(src, dest):
        return None
    if not is_source_town and not _is_crossable(src, dest, neighbors=neighbors):
        return None

    l = 1.414 if src.is_diagonal(dest) else 1
    c = _forest_cost(src, dest)
    p = _height_penalty(abs(src.alt - dest.alt))

    if dest.is_sea:
        return l
    return l * c + p

def is_crossable_if_source_is_town(src: TileInfo, dest: TileInfo) -> bool:
    # Cases: ⬜ = town
    # 
    # 1) ⬜ 🟩   2) ⬜ 🟩
    #    🟩 🟦      🟦 🟦
    # 3) ⬜ 🟦   4) ⬜ 🟦
    #    🟩 🟦      🟦 🟦

    if not src.is_adjacent(dest):
        return False
    return True
    
def _is_crossable(src: TileInfo, dest: TileInfo, neighbors: Sequence[TileInfo] = ()) -> bool:
    # Land transports can travel in diagonals even if the other tiles in the 2x2 square are water, but the same doesnt apply to sea transports
    # Ex: land can travel this way (bottom left to top right)
    # 🟦 🟩 
    # 🟩 🟦 
    # But sea transports cant travel from bottom right to top left
    # > Just to confirm, in this case top left to bottom right is allowed, right?
    # > 🟦 🟦
    # > 🟩 🟦
    # For sea travel yes

    if not src.is_adjacent(dest):
        return False
    if src.is_sea != dest.is_sea:
        return False
    if not src.is_diagonal(dest):
        return True
    if not src.is_sea and not dest.is_sea:
        return True
    for n in neighbors:
        if n.is_sea:
            return True
    return False

def _forest_cost(src: TileInfo, dest: TileInfo) -> float:
    if src.is_forest and dest.is_forest:
        return 2
    if src.is_forest or dest.is_forest:
        return 1.5
    return 1

def _height_penalty(height: int) -> float:
    if height < 25:
        return 0
    if height < 75:
        return 2
    if height < 125:
        return 5
    return 20

def convert(arr: Sequence[int | None]) -> Tile:
    return Tile(
        x=arr[0],
        y=arr[1],
        alt=arr[2],
        fertility=arr[3],
        forest=arr[4],
        res=arr[5],
        res_amount=arr[6],
        region=arr[7],
        area=arr[8],
        type=arr[9],
    )