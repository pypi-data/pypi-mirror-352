import functools
import xarray as xr
from importlib_resources import files


@functools.cache
def _read_coeffs(file):
    return xr.open_dataset(files('meuvm._coeffs').joinpath(file))


def get_meuvm_ba():
    return _read_coeffs('_meuvm_ba_coeffs.nc').copy()


def get_meuvm_r():
    return _read_coeffs('_meuvm_r_coeffs.nc').copy()


def get_meuvm_br():
    return _read_coeffs('_meuvm_br_coeffs.nc').copy()
