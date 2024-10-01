# Mercatorio distance map calculator

This repo provides a base library for computing travel distances by land and by sea starting from a given point on the map to any other reachable point on the map. The given point is assumed to be a town.

Under the hood, it uses [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm):

> Dijkstra's algorithm finds the shortest path from a given source node to every other node.

It uses native python libraries, so no other requirement is needed (apart from Python 3 installed).

## Intended usage

Several community created websites (like [this one](https://king-br.github.io/Mercatorio-Interactive-Map/)) are providing a glympse of how far you can reach with a transportation. Unfortunately there's not yet a simple way of showing actual possible travel distances live in the browser due to the size of the map.

This library is intended to provide an offline computation of distances from each city (one at a time). Given a transportation vehicle and its range, it is then possible to show only the tiles within travel range.

## Architecture

Dijkstra's algorithm finds the shortest path from a given source node to every other node of a graph.

In our case, the graph is the whole Mercatorio map. Each node is a tile. Each node is connected (i.e. potentially traversable) to any other node vertically, horizontally and diagonally.

For optimization reasons, tiles are uniquely identify by the attribute `key` which is the python hash of their coordinates (`hash((x, y))`).
With this in mind, it is hence unnecessary to build any additional datastructure to track edges of the graph, as they are known before hand (i.e. node `x, y` is connected to `x+1, y`,  `x, y+1`,  `x+1, y+1` and so on, except when sitting on the boundaries of the map).

Travel costs are computed in two steps:
1. First the map is loaded and the weights of the individual edges (i.e. individual moves between two tiles) are computed.
2. The Dijkstra's algorithm is applied on the map of weights from the given source node.

### Move costs

As of season 2, the cost of a move is determined as the following (according to discussions on the official Discord server):
- Land movement cost: The cost of one move is `l * c + p` where 
    - `c` is cost of passing through forest (`1` for no forest, `1.5` if one plot has forest and `2` if both origin and destination has)
    - `p` is altitude penalty (`0` for altitude *difference* <25m, `2` for <75m, `5` for <125m and `20` >= 125m)
    - `l` (length) is `1` for straight moves and `1.414` for diagonal ones.
- Sea movement cost: `l`, where `l` is `1` for straigh move and `1.414` for diagonals

### Crossability/Traversability

Despite two tiles being connected (i.e. *potentially* traversable), it doesn't mean the move between the two is allowed by the game.
Indeed there are a series of constraints which must be **all** satisfied for a move to be allowed:
- Except for towns, tiles must be of the same type (i.e. both land or both sea)
- If two tiles are vertically or horizontally connected, a move is always allowed.
- If two **land** tiles are diagonally connected, a move is always allowed.
- If two **sea** tiles are diagonally connected, a move is always allowed only if another **sea** tile is adjacent to **both**.

In our library if a move between two tiles is not allowed (or does not exist like at the boundaries of the map), its weight is `None`.

## Limitations

- Ferries are not yet supported. Mainly due to lack of knowledge of how they work yet.
- Currently no map areas are taken into account for the map traversability. It is not yet clear how areas affect it in the game.
