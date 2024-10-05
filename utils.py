import gzip
import json
import zipfile
from lib.types import TileInfo
from lib.utils import convert
import os.path
from typing import Sequence

# How compressed map is unachived
SINGLE_FILE_MAP_FILE = 'map_data.json'
# How uncompressed map is unachived
MULTI_FILE_MAP = [
    'plots_0.json',
    'plots_1.json',
    'plots_2.json',
    'plots_3.json',
]

def _map_json_path(map_dir: str, file_path: str) -> str:
    return f'{map_dir}/{file_path}'

def _compressed_map_json_path(map_dir: str) -> str:
    return _map_json_path(map_dir, SINGLE_FILE_MAP_FILE)

def decompress(map_archive: str, map_output_dir: str) -> None:
    if 'gz' in map_archive:
        _decompress_zip(map_archive, map_output_dir)
    else:
        _decompress_gz(map_archive, _compressed_map_json_path(map_output_dir))

def _decompress_zip(infile: str, todir: str):
    with zipfile.ZipFile(infile, 'r') as zip_ref:
        zip_ref.extractall(todir)

def _decompress_gz(infile: str, tofile: str):
    with open(infile, 'rb') as inf, open(tofile, 'w', encoding='utf8') as tof:
        decom_str = gzip.decompress(inf.read()).decode('utf-8')
        tof.write(decom_str)

def load_json(json_path: str) -> dict | list:
    with open(json_path) as fd:
        json_data = json.load(fd)
    return json_data

def load_map(map_dir: str) -> Sequence[TileInfo]:
    print('Loading map...')
    if os.path.isfile(_compressed_map_json_path(map_dir)):
        json_data = load_json(_compressed_map_json_path(map_dir))
        return [convert(entry) for entry in json_data]
    else:
        for f in MULTI_FILE_MAP:
            assert(os.path.isfile(_map_json_path(map_dir, f)))
        return [
            convert(entry) for entry in load_json(f)
            for f in MULTI_FILE_MAP
        ]
