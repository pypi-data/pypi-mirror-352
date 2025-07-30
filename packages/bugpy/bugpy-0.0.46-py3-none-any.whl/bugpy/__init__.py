from .db_manager import Connection
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution('bugpy').version
    print(f"Loaded bugpy version v{__version__}")
except:
    __version__ = 'debug'
    print("Using local version of bugpy for debug and development")
