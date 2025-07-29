import numpy as np
import xarray as xr
import meuvm._misc as _m


class MeuvmBr:
    '''
    MEUVM Binned Regression model class.
    '''

    def __init__(self):
        self._dataset = _m.get_meuvm_br()
        self._coeffs = np.array(self._dataset[['k0', 'b0', 'k1', 'b1', 'k2', 'b2', 'k3', 'b3', 'k4', 'b4',
                                               'k5', 'b5', 'k6', 'b6', 'k7', 'b7', 'k8', 'b8', 'k9', 'b9',
                                               'k10', 'b10']].to_dataarray()).T

    def _calc_spectra(self, _f107):
        spectra = np.empty((190, 0))
        for f107 in _f107:
            if f107 <= 80:
                i = 0
            elif 80 < f107 <= 100:
                i = 1
            elif 100 < f107 <= 120:
                i = 2
            elif 120 < f107 < 140:
                i = 3
            elif 140 < f107 < 160:
                i = 4
            elif 160 < f107 < 180:
                i = 5
            elif 180 < f107 < 200:
                i = 6
            elif 200 < f107 < 220:
                i = 7
            elif 220 < f107 < 240:
                i = 8
            elif 240 < f107 < 260:
                i = 9
            elif f107 > 260:
                i = 10

            f107 = np.array([f107, 1.], dtype=np.float64).reshape(1, 2)
            coeffs = np.array(self._coeffs[:, i*2:i*2+2])
            spectrum = np.dot(coeffs, f107.T)
            spectra = np.hstack([spectra, spectrum])
        return spectra

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
            f107 = np.array([f107], dtype=np.float64) if isinstance(f107, (int, float)) \
                else np.array(f107, dtype=np.float64)

        res = self._calc_spectra(f107)
        return xr.Dataset(data_vars={'euv_flux_spectra': (('band_center', 'f107'), res),
                                     'lband': ('band_number', self._dataset['lband'].values),
                                     'uband': ('band_number', self._dataset['uband'].values)},
                          coords={'f107': f107,
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
