import pkg_resources

__version__ = "2.0.0"
__version_info__ = tuple(int(i) for i in __version__ if i.isdigit())


pkg_resources.declare_namespace(__name__)
