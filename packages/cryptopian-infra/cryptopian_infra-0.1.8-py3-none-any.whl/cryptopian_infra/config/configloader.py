import inspect
import json
import os

from jsmin import jsmin


def relative_path_from_cur_dir(relative_path):
    file_path = inspect.stack()[1][1]
    return os.path.abspath(os.path.join(os.path.dirname(file_path), relative_path))


def load_json_config(json_config_file_path: str, encoding: str = 'utf-8') -> dict:
    with open(json_config_file_path, encoding=encoding) as f:
        return json.load(f)


def load_json_config_with_comment(json_config_file_path: str, encoding: str = 'utf-8') -> dict:
    with open(json_config_file_path, encoding=encoding) as f:
        return json.loads(jsmin(f.read()))


def load_config(relative_path: str, encoding: str = 'utf-8') -> dict:
    file_path = inspect.stack()[1][1]
    p = os.path.abspath(os.path.join(os.path.dirname(file_path), relative_path))
    with open(p, encoding=encoding) as f:
        return json.load(f)
