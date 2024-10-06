import json
from lib.map import TileMap
from lib.types import TileDistance
import os.path
from typing import Sequence
from utils import decompress, load_json, load_map, load_ferries, retrieve_or_update_ferries
from urllib.request import urlretrieve

# MAP_ARCHIVE = 'map_compressed.gz' # Currently missing some tiles for some reason.
MAP_ARCHIVE = 'compressed.zip'
MAP_DIR = 'map'
TOWN_JSON = 'towns_s2.json'
FERRIES_JSON = 'ferries.json'

def save_distances(town_name: str, distances: Sequence[TileDistance]) -> None:
    # Convert to compressed format
    compressed = [[d.x, d.y, d.distance] for d in distances]

    file_name = f'{town_name}.json'
    with open(file_name, 'w', encoding='utf8') as fp:
        fp.write(json.dumps(compressed))
    print(f'Town distances file saved as {file_name}')

# If MAP_DIR doesn't exists yet or is still empty
if not os.path.isdir(MAP_DIR) or not os.listdir(MAP_DIR):
    decompress(MAP_ARCHIVE, MAP_DIR)

retrieve_or_update_ferries(FERRIES_JSON)

towns = load_json(TOWN_JSON)
ferries = load_ferries(FERRIES_JSON)
map = TileMap(load_map(MAP_DIR), ferries=ferries)
map.compute_costs()

for t in towns:
    town_name: str = t['name']
    print(f'Town: {town_name}')
    x: int = t['location']['x']
    y: int = t['location']['y']

    dist = map.compute_distances(x, y)

    save_distances(town_name.lower(), dist)
