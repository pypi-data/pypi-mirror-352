import sys
import pysnmp

try:
    # Python 3.8+
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For Python <3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    pysnmp_version = version("pysnmplib")
    raise ImportError(
        f"pysnmp-sync-adapter requires pysnmp>=7.0.0. "
        f"Detected version: pysnmplib {pysnmp_version}. "
        f"Please uninstall pysnmplib with `pip uninstall pysnmplib`. "
        f"Then install the latest pysnmp version with `pip install pysnmp`."
    )
except PackageNotFoundError:
    pass

try:
    pysnmp_version = version("pysnmp")
    if pysnmp_version.startswith("4.") or pysnmp_version.startswith("5."):
        raise ImportError(
            f"pysnmp-sync-adapter requires pysnmp>=7.0.0. "
            f"Detected version: {pysnmp_version}. "
            f"Please uninstall pysnmp with `pip uninstall pysnmp`. "
            f"Then install the latest pysnmp version with `pip install pysnmp`."
        )
except PackageNotFoundError:
    print("pysnmp not found. Please install pysnmp>=7.0.0.", file=sys.stderr)
    raise

from .sync_adapters import (
    get_cmd_sync,
    next_cmd_sync,
    set_cmd_sync,
    bulk_cmd_sync,
    walk_cmd_sync,
    bulk_walk_cmd_sync,
    create_transport,
    parallel_get_sync,
    cluster_varbinds
)
