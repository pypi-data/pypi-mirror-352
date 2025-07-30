"""AstroWISP python interface."""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'astrowisp.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from os import path

from astrowisp.background import BackgroundExtractor
from astrowisp.fit_star_shape import FitStarShape
from astrowisp.subpixphot import SubPixPhot
from astrowisp.io_tree import IOTree
from astrowisp.piecewise_bicubic_psf_map import PiecewiseBicubicPSFMap
from astrowisp.piecewise_bicubic_psf import PiecewiseBicubicPSF

_module_path = path.dirname(path.abspath(__file__))

fistar_path = path.join(_module_path, 'fistar')
if not path.exists(fistar_path):
    fistar_path += '.exe'
assert path.exists(fistar_path)

__all__ = ['BackgroundExtractor',
           'FitStarShape',
           'SubPixPhot',
           'PiecewiseBicubicPSF',
           'PiecewiseBicubicPSFMap']