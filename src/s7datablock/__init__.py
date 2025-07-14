import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "s7datablock"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

# Export public API
from s7datablock.fields import S7Field
from s7datablock.mapping import BufferMapping, S7DataBlock
from s7datablock.parser import parse_db_file

__all__ = ["S7Field", "BufferMapping", "S7DataBlock", "parse_db_file"]
