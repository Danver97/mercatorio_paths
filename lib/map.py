from __future__ import annotations
import heapq
from lib.types import FerryInfo, TileDistance, TileWeight, hash_coords, MAX_HEIGHT
from lib.utils import compute_weight, is_crossable_if_source_is_town, size_logger
import sys
from typing import Sequence

class TileMap:
    def __init__(self, tiles: Sequence[TileWeight], ferries: Sequence[FerryInfo] = ()):
        self._map = {
            t.key: t for t in tiles
        }
        for f in ferries:
            self._map[f.key].ferries = f.ferries
        size_logger('Map loaded. Total size in RAM: {size} GB', self._map, unit='GB')
        # print(f'Map loaded. Total size in RAM: {asizeof(self._map)/1024/1024/1024} GB')

    def compute_costs(self) -> None:
        print('Computing costs...')
        for i, w in enumerate(self._map.values()):
            try:
                if w.up_key is not None:
                    w.up_weight = compute_weight(self._map[w.key], self._map[w.up_key])
                if w.left_key is not None:
                    w.left_weight = compute_weight(self._map[w.key], self._map[w.left_key])
                if w.right_key is not None:
                    w.right_weight = compute_weight(self._map[w.key], self._map[w.right_key])
                if w.down_key is not None:
                    w.down_weight = compute_weight(self._map[w.key], self._map[w.down_key])
                if w.up_left_key is not None:
                    w.up_left_weight = compute_weight(self._map[w.key], self._map[w.up_left_key], neighbors=(self._map[w.up_key], self._map[w.left_key]))
                if w.up_right_key is not None:
                    w.up_right_weight = compute_weight(self._map[w.key], self._map[w.up_right_key], neighbors=(self._map[w.up_key], self._map[w.right_key]))
                if w.down_left_key is not None:
                    w.down_left_weight = compute_weight(self._map[w.key], self._map[w.down_left_key], neighbors=(self._map[w.down_key], self._map[w.left_key]))
                if w.down_right_key is not None:
                    w.down_right_weight = compute_weight(self._map[w.key], self._map[w.down_right_key], neighbors=(self._map[w.down_key], self._map[w.right_key]))
            except:
                print(f'Failed when processing weight {w.x} {w.y}')
                raise
            if i % MAX_HEIGHT == 0:
                print(f'Processed {i // MAX_HEIGHT} rows of the map')
        size_logger('Costs computed. Total size in RAM: {size} GB', self._map, unit='GB')
        # print(f'Costs computed. Total size in RAM: {asizeof(self._map)/1024/1024/1024} GB')

    def dijkstra(self, x: int, y: int) -> dict[int, float]:
        print('Running djkstra...')
        pq = []
        dist: dict[int, float] = {}

        source_key = hash_coords(x, y)

        for k in self._map.keys():
            if k == source_key:
                dist[source_key] = 0
                heapq.heappush(pq, (0, k))
            else:
                dist[k] = sys.float_info.max

        while len(pq) > 0:
            # define u ← vertex in Q with minimum dist[u]
            _, u = heapq.heappop(pq)

            # For each neighbor of u
            for n in self._map[u].adjacency_keys:
                distance_u_n = self._map[u].distance(n)
                # If distance_u_n is None, u and n are not crossable, mostly because is a land -> sea move.
                # But if we are starting from a town, we can go whenever we want (i.e. land -> sea is allowed as we are boarding).
                # In such a case, the initial weight is 0 as we are starting from the sea tile with the boat.
                if distance_u_n is None and u == source_key and is_crossable_if_source_is_town(self._map[u], self._map[n]):
                    distance_u_n = 0

                # distance_u_n is still None, u and n are not connected in the graph
                if distance_u_n is None:
                    continue

                alt = dist[u] + distance_u_n
                if alt < dist[n]:
                    dist[n] = alt
                    heapq.heappush(pq, (alt, n))
        return dist
    
    def compute_distances(self, x: int, y: int) -> Sequence[TileDistance]:
        dist = self.dijkstra(x, y)
        return [
            TileDistance(t.x, t.y, dist[t.key] if dist[t.key] != sys.float_info.max else None)
                for t in self._map.values()
                if dist[t.key] != sys.float_info.max
            ]
