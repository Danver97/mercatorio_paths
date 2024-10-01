from __future__ import annotations
from dataclasses import dataclass
import heapq
import sys
from typing import Sequence

MAX_HEIGHT = 4096
MAX_WIDTH = 4096

def hash_coords(x: int, y: int) -> int:
    return hash((x, y))

@dataclass(frozen=True)
class Tile:
    x: int
    y: int
    
    def _safe_hash(self, x: int, y: int) -> int | None:
        if x >= 0 and x < MAX_WIDTH and y >= 0 and y < MAX_HEIGHT:
            return hash_coords(x, y)
        return None
    
    @property
    def key(self) -> int:
        return hash_coords(self.x, self.y)
    
    @property
    def adjacency_keys(self) -> Sequence[int]:
        return list(filter(lambda k: k is not None, [
            self.up_key,
            self.left_key,
            self.right_key,
            self.down_key,
            self.up_left_key,
            self.up_right_key,
            self.down_left_key,
            self.down_right_key,
        ]))

    @property
    def up_key(self) -> int | None:
        return self._safe_hash(self.x, self.y - 1)
    
    @property
    def left_key(self) -> int | None:
        return self._safe_hash(self.x - 1, self.y)
    
    @property
    def right_key(self) -> int | None:
        return self._safe_hash(self.x + 1, self.y)
    
    @property
    def down_key(self) -> int | None:
        return self._safe_hash(self.x, self.y + 1)
    
    @property
    def up_left_key(self) -> int | None:
        return self._safe_hash(self.x - 1, self.y - 1)
    
    @property
    def up_right_key(self) -> int | None:
        return self._safe_hash(self.x + 1, self.y - 1)
    
    @property
    def down_left_key(self) -> int | None:
        return self._safe_hash(self.x - 1, self.y + 1)
    
    @property
    def down_right_key(self) -> int | None:
        return self._safe_hash(self.x + 1, self.y + 1)
    
    def is_adjacent(self, other: Tile) -> bool:
        return other.key in (
            self.up_key,
            self.left_key,
            self.right_key,
            self.down_key,
            self.up_left_key,
            self.up_right_key,
            self.down_left_key,
            self.down_right_key,
        )
    
    def is_diagonal(self, other: Tile) -> bool:
        return other.key in (
            self.up_left_key,
            self.up_right_key,
            self.down_left_key,
            self.down_right_key,
        )

@dataclass(frozen=True)
class TileInfo(Tile):
    alt: int # altitude (type is integer)
    fertility: int # tile fertility, 0 is arid, less than 40 is grazing, less than 80 is fertile, 80 or higher is clay (type is integer)
    forest: int | None # if the property exists, the tile has a forest (type is a integer)
    res: int | None # type of resource, if it doesnt exists the tile doesnt have a resource (type is integer)
    res_amount: int | None # not used in-game (type is integer)
    region: int | None # in-game region, can ignore for pathfinding
    area: int | None # this property defines a navigable area, if it doesnt exists, the tile is unnavigable (type is integer)
    type: int | None # if the property exists, the tile is a water tile (type is integer)

    @property
    def is_sea(self) -> bool:
        return self.type is not None
    
    @property
    def is_forest(self) -> bool:
        return self.forest is not None

class TileWeight(Tile):
    up_weight: int | None
    left_weight: int | None
    right_weight: int | None
    down_weight: int | None
    up_left_weight: int | None
    up_right_weight: int | None
    down_left_weight: int | None
    down_right_weight: int | None

    def distance(self, key: int) -> int | None:
        if key == self.up_key:
            return self.up_weight
        if key == self.left_key:
            return self.left_weight
        if key == self.right_key:
            return self.right_weight
        if key == self.down_key:
            return self.down_weight
        if key == self.up_left_key:
            return self.up_left_weight
        if key == self.up_right_key:
            return self.up_right_weight
        if key == self.down_left_key:
            return self.down_left_weight
        if key == self.down_right_key:
            return self.down_right_weight
        return None

@dataclass(frozen=True)
class TileDistance(Tile):
    distance: int | None