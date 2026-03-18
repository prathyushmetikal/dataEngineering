# pkg_resources/__init__.py
import importlib.metadata as metadata

class Distribution:
    def __init__(self, name):
        self.name = name
        self.version = metadata.version(name)

def get_distribution(name):
    return Distribution(name)

def require(name):
    return [get_distribution(name)]