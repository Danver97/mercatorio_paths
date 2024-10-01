import gzip
import json
from lib.map import TileMap
from lib.types import TileDistance, TileInfo
from lib.utils import convert
import os.path
from typing import Sequence

MAP_ARCHIVE = 'map_compressed.gz'
MAP_JSON = 'map/map_decompressed.json'
TOWN_JSON = 'towns_s2.json'

def decompress(infile: str, tofile: str):
    with open(infile, 'rb') as inf, open(tofile, 'w', encoding='utf8') as tof:
        decom_str = gzip.decompress(inf.read()).decode('utf-8')
        tof.write(decom_str)

def load_json(json_path: str) -> dict | list:
    with open(json_path) as fd:
        json_data = json.load(fd)
    return json_data

def load_map(json_path: str) -> Sequence[TileInfo]:
    print('Loading map...')
    json_data = load_json(json_path)
    
    return [convert(entry) for entry in json_data]

def save_distances(town_name: str, distances: Sequence[TileDistance]) -> None:
    # Convert to compressed format
    compressed = [[d.x, d.y, d.distance] for d in distances]

    file_name = f'{town_name}.json'
    with open(file_name, 'w', encoding='utf8') as fp:
        fp.write(json.dumps(compressed))
    print(f'Town distances file saved as {file_name}')

if not os.path.isfile(MAP_JSON):
    decompress(MAP_ARCHIVE, MAP_JSON)

towns = load_json(TOWN_JSON)
map = TileMap(load_map(MAP_JSON))
map.compute_costs()

for t in towns:
    town_name: str = t['name']
    print(f'Town: {town_name}')
    x: int = t['location']['x']
    y: int = t['location']['y']

    dist = map.compute_distances(x, y)

    save_distances(town_name.lower(), dist)
