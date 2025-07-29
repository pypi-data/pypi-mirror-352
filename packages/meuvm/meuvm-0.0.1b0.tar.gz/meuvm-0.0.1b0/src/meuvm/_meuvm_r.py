import numpy as np
import xarray as xr
import meuvm._misc as _m


class MeuvmR:
    '''
    MEUVM Regression model class.
    '''

    def __init__(self):
        self._dataset = _m.get_meuvm_r()
        self._coeffs = np.array(np.vstack([self._dataset['b0'],
                                           self._dataset['b1']])).T

    def _get_f(self, f107):
        try:
            if isinstance(f107, float) or isinstance(f107, int):
                return np.array([f107, 1.0], dtype=np.float64).reshape(1, 2)
            return np.vstack([np.array([x, 1.0]) for x in f107], dtype=np.float64)
        except TypeError:
            raise TypeError('Only int, float or array-like object types are allowed.')

    def _check_types(self, f107):
        if isinstance(f107, (float, int, np.integer, list, np.ndarray)):
            if isinstance(f107, (list, np.ndarray)):
                if not all([isinstance(x, (float, int, np.integer)) for x in f107]):
                    raise TypeError(
                        f'Only float and int types are allowed in array.')
        else:
            raise TypeError(f'Only float, int, list and np.ndarray types are allowed. f107 was {type(f107)}')
        return True

    def get_spectral_bands(self, f107):
        if self._check_types(f107):
            x = self._get_f(f107)

        res = np.dot(self._coeffs, x.T)
        return xr.Dataset(data_vars={'euv_flux_spectra': (('band_center', 'f107'), res),
                                     'lband': ('band_number', self._dataset['lband'].values),
                                     'uband': ('band_number', self._dataset['uband'].values)},
                          coords={'f107': x[:, 0],
                                  'band_center': self._dataset['center'].values,
                                  'band_number': np.arange(190)},
                          attrs={'F10.7 units': '10^-22 · W · m^-2 · Hz^-1',
                                 'spectra units': 'W · m^-2 · nm^-1',
                                 'wavelength units': 'nm',
                                 'euv_flux_spectra': 'modeled EUV solar irradiance',
                                 'lband': 'lower boundary of wavelength interval',
                                 'uband': 'upper boundary of wavelength interval'})

    def get_spectra(self, f107):
        return self.get_spectral_bands(f107)

    def predict(self, f107):
        return self.get_spectral_bands(f107)
