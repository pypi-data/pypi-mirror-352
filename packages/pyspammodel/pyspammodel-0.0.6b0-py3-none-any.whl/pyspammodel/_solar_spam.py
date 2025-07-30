import numpy as np
import xarray as xr
import pyspammodel._misc as _m


class SolarSpam:
    '''
    Solar-SPAM model class.
    '''
    def __init__(self):
        self._dataset = _m.get_solar_spam_coeffs()
        self._coeffs = np.vstack((np.array(self._dataset['P1'], dtype=np.float64),
                                  np.array(self._dataset['P2'], dtype=np.float64),
                                  np.array(self._dataset['P3'], dtype=np.float64))).transpose()

    def _get_f107(self, f107):
        '''
        Method for creating the daily F10.7 index matrix that will be used to calculate the spectrum.
        Returns a matrix with rows [F10.7 ^ 2; F10.7; 1] for each passed value F10.7.
        :param f107: single value of the daily index F10.7 or an array of such values.
        :return: numpy array for model calculation.
        '''
        try:
            if isinstance(f107, float) or isinstance(f107, int):
                return np.array([f107 ** 2, f107, 1], dtype=np.float64).reshape(1, 3)
            return np.vstack([np.array([x ** 2, x, 1]) for x in f107], dtype=np.float64)
        except TypeError:
            raise TypeError('Only int, float or array-like object types are allowed')

    def _predict(self, matrix_a, vector_x):
        return np.dot(matrix_a, vector_x)

    def get_spectral_bands(self, f107):
        '''
        Model calculation method. Returns the xarray dataset values of radiation fluxes in all intervals
        of the spectrum of the interval 0-190 nm
        :param f107: single value of the daily index F10.7 or an array of such values
        :return: xarray Dataset [euv_flux_spectra, line_lambda]
        '''
        f107 = self._get_f107(f107)
        res = self._predict(self._coeffs, f107.T)
        return xr.Dataset(data_vars={'euv_flux_spectra': (('band_center', 'F107'), res),
                                     'lband': ('band_number', np.arange(0, 190)),
                                     'uband': ('band_number', np.arange(1, 191))},
                          coords={'F107': f107[:, 1],
                                  'band_center': self._dataset['lambda'].values,
                                  'band_number': np.arange(190)},
                          attrs={'F10.7 units': '10^-22 · W · m^-2 · Hz^-1',
                                 'spectra units': 'W · m^-2 · nm^-1',
                                 'wavelength units': 'nm',
                                 'euv_flux_spectra': 'modeled EUV solar irradiance',
                                 'lband': 'lower boundary of wavelength interval',
                                 'uband': 'upper boundary of wavelength interval'})

    def get_spectra(self, f107):
        '''
        Model calculation method. Used to unify the interface with AeroSpam class.
        :param f107: single value of the daily index F10.7 or an array of such values.
        :return: xarray Dataset [euv_flux_spectra, line_lambda]
        '''
        return self.get_spectral_bands(f107)
