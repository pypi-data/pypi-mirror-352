import os.path
import warnings
from pathlib import Path

import yaml


class Loader(yaml.Loader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node):
        file_name = os.path.join(self._root, self.construct_scalar(node))
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding="utf-8") as f:
                return yaml.load(f, Loader)
        else:
            return {}


Loader.add_constructor('!include', Loader.include)


def load(file_name):
    file_path = Path(file_name).expanduser().absolute()
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as fr:
            dict_obj = yaml.load(fr, Loader=Loader)
        return dict_obj
    else:
        warnings.warn("<UNK>{}".format(file_path))
        return {}
