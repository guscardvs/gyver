__version__ = "4.1.7"
__version_info__ = tuple(int(i) for i in __version__ if i.isdigit())


__path__ = __import__("pkgutil").extend_path(__path__, __name__)
