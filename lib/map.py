from __future__ import annotations
import heapq
from lib.types import TileDistance, TileInfo, TileWeight, hash_coords
from lib.utils import compute_weight, is_crossable_if_source_is_town
import sys
from typing import Sequence

class TileMap:
    def __init__(self, tiles: Sequence[TileInfo]):
        self._map = {
            t.key: t for t in tiles
        }
        self.weights = {
            t.key: TileWeight(x=t.x, y=t.y) for t in tiles
        }

    def compute_costs(self) -> None:
        for w in self.weights.values():
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

    def dijkstra(self, x: int, y: int) -> dict[int, float]:
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
                distance_u_n = None
                # If we are starting from a town, we can go whenever we want (i.e. land -> sea is allowed as we are boarding)
                # In such a case, we compute the initial weight on the fly as in the case of a land -> sea move, we treated the graph as disconnected.
                if u == source_key and is_crossable_if_source_is_town(self._map[u], self._map[n]):
                    distance_u_n = compute_weight(self._map[u], self._map[n], is_source_town=True)
                else:
                    distance_u_n = self.weights[u].distance(n)

                # distance_u_n is None, u and n are not connected in the graph (basically _is_crossable returned False)
                if distance_u_n is None:
                    continue

                alt = dist[u] + distance_u_n
                if alt < dist[n]:
                    dist[n] = alt
                    heapq.heappush(pq, (alt, n))
        return dist
    
    def compute_distances(self, x: int, y: int) -> Sequence[TileDistance]:
        dist = self.dijkstra(x, y)
        return [TileDistance(t.x, t.y, dist[t.key] if dist[t.key] != sys.float_info.max else None) for t in self._map.values()]