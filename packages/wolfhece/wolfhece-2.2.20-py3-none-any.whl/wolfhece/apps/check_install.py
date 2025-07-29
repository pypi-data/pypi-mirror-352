
"""
Author: HECE - University of Liege, Pierre Archambeau
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""

def main():
    # Check if installation is complete
    ret = 'Checking installation\n---------------------\n\n'


    # Get list of all packages
    import pkg_resources
    installed_packages = pkg_resources.working_set
    packages = sorted(["%s" % (i.key) for i in installed_packages])

    #is osgeo in packages?
    if 'osgeo' in packages or 'gdal' in packages:
        ret += 'OSGeo seems installed\n\n'
    else:
        ret += 'OSGeo not installed\n Please install GDAL from https://github.com/cgohlke/geospatial-wheels/releases\n\n'

    try:
        from osgeo import ogr, gdal
        ret += 'Correct import of osgeo package - GDAL/OGR installed\n\n'
    except ImportError as e:
        ret += 'Error during osgeo import - GDAL/OGR not/bad installed\n Please (re)install GDAL (64 bits version) from https://github.com/cgohlke/geospatial-wheels/releases\n\n'
        ret += 'Error : ' + str(e) + '\n\n'

    if 'wolfgpu' in packages:
        ret += 'WolfGPU seems installed\n\n'
    else:
        ret += 'WolfGPU not installed\n Please install WolfGPU if needed\n\n'

    # try:
    #     from ..libs import wolfpy
    #     ret += 'Wolfpy accessible\n\n'
    # except ImportError as e:
    #     ret += 'Wolfpy not accessible\n\n'
    #     ret += 'Error : ' + str(e) + '\n\n'

    try:
        from ..PyGui import MapManager
        ret += 'Wolfhece installed\n\n'
    except ImportError as e:
        ret += 'Wolfhece not installed properly\n Retry installation : pip install wolfhece or pip install wolfhece --upgrade\n\n'
        ret += 'Error : ' + str(e) + '\n\n'

    try:
        from ..lazviewer.processing.estimate_normals.estimate_normals import estimate_normals
    except ImportError as e:
        ret += 'Could not import estimate_normals\n\n'
        ret += 'Wolfhece not installed properly\n Please install the VC++ redistributable\n from https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads\n\n'
        ret += 'Error : ' + str(e) + '\n\n'

    from pathlib import Path
    dirlaz = Path(__file__).parent.parent / 'lazviewer'
    dirs_to_test =  [dirlaz / 'libs', dirlaz / 'libs/qt_plugins', dirlaz / 'libs/qt_plugins/platforms']

    for d in dirs_to_test:
        if not d.exists() or not d.is_dir():
            ret += str(d) + ' does not exist\n\n'

    curdir = dirlaz / 'libs/qt_plugins/platforms'
    files_to_test = [curdir / 'qwindows.dll']

    for f in files_to_test:
        if not f.exists() or not f.is_file():
            ret += str(f) + ' does not exist\n\n'

    curdir = dirlaz / 'libs'
    files_to_test = [curdir / 'icudt53.dll', curdir / 'icuin53.dll', curdir / 'icuuc53.dll',
                     curdir / 'msvcp120.dll', curdir / 'msvcr120.dll', curdir / 'Qt5Core.dll',
                     curdir / 'Qt5Gui.dll', curdir / 'Qt5Network.dll', curdir / 'Qt5Widgets.dll',
                     curdir / 'tbb.dll', curdir / 'tbbmalloc.dll', curdir / 'vcomp120.dll']

    for f in files_to_test:
        if not f.exists() or not f.is_file():
            ret += str(f) + ' does not exist\n\n'

    try:
        from ..lazviewer.viewer import viewer
        import numpy as np

        pts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        myview = viewer.viewer(pts, debug = True)

        ret += 'LAZ viewer created in debug mode -- check for errors if reported\n\n'

    except ImportError as e:
        ret += 'Could not import/create LAZ viewer\n\n'
        ret += 'Wolfhece not installed properly\n Please check if QT \n\n'
        ret += 'Error : ' + str(e) + '\n\n'

    print(ret)

if __name__=='__main__':
    main()