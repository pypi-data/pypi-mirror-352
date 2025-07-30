import functools
import xarray as xr
from importlib_resources import files


@functools.cache
def read_coeffs(file):
    return xr.open_dataset(files('pyspammodel._coeffs').joinpath(file))


def get_aero_spam_coeffs():
    return (read_coeffs('_aero_spam_bands_coeffs.nc').copy(), read_coeffs('_aero_spam_lines_coeffs.nc').copy(),
            read_coeffs('_aero_spam_full_coeffs.nc').copy())


def get_solar_spam_coeffs():
    return read_coeffs('_solar_spam_coeffs.nc').copy()
