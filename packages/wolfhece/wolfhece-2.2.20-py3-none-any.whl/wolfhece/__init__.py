from . import _add_path
from .PyTranslate import _

try:
    from osgeo import gdal, osr, ogr
    gdal.UseExceptions()
    ogr.UseExceptions()
    osr.UseExceptions()
except ImportError as e:
    # print(e)
    raise Exception(_('Error importing GDAL library\nPlease ensure GDAL is installed and the Python bindings are available\n\ngdal wheels can be found at https://github.com/cgohlke/geospatial-wheels'))

from .apps.version import WolfVersion
from packaging.version import Version

__version__ = WolfVersion().get_version()

def is_enough(version: str) -> bool:
    """
    Compare the current version of WolfHece to a given version string.

    Args:
        version (str): The version string to compare against.

    Returns:
        bool: True if the current version is greater than or equal to the given version, False otherwise.
    """
    return Version(__version__) >= Version(version)