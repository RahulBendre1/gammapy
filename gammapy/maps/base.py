# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
import abc
import numpy as np
from astropy.extern import six
from astropy.utils.misc import InheritDocstrings

__all__ = [
    'MapBase',
]


class MapMeta(InheritDocstrings, abc.ABCMeta):
    pass


@six.add_metaclass(MapMeta)
class MapBase(object):
    """Abstract map class.

    This can represent WCS- or HEALPIX-based maps
    with 2 spatial dimensions and N non-spatial dimensions.

    Parameters
    ----------
    geom : `~gammapy.maps.geom.MapGeom`

    data : `~numpy.ndarray`
    """

    def __init__(self, geom, data):
        self._data = data
        self._geom = geom
        self._iter = None

    @property
    def data(self):
        """Array of data values."""
        return self._data

    @property
    def geom(self):
        return self._geom

    @data.setter
    def data(self, val):
        if val.shape != self.data.shape:
            raise Exception('Wrong shape.')
        self._data = val

    @classmethod
    def create(cls, **kwargs):
        """Create a new empty map object.

        Parameters
        ----------
        map_type : str
            Internal map representation.  Valid types are `wcs`,
            `wcs-sparse`,`hpx`, and `hpx-sparse`.

        """

        from .hpxmap import HpxMap
        from .wcsmap import HpxMap

        map_type = kwargs.setdefault('map_type', 'wcs')

        if 'wcs' in map_type.lower():
            return WcsMap.create(**kwargs)
        elif 'hpx' in map_type.lower():
            return HpxMap.create(**kwargs)
        else:
            raise ValueError('Unrecognized map type: {}'.format(map_type))

    def __iter__(self):
        return self

    def __next__(self):

        if self._iter is None:
            self._iter = np.ndenumerate(self.data)

        try:
            return next(self._iter)
        except StopIteration:
            self._iter = None
            raise

    next = __next__

    @abc.abstractmethod
    def sum_over_axes(self):
        """Reduce to a 2D image by dropping non-spatial dimensions."""
        pass

    @abc.abstractmethod
    def get_by_coords(self, coords, interp=None):
        """Return map values at the given map coordinates.

        Parameters
        ----------
        coords : tuple or `~gammapy.maps.geom.MapCoords`
            `~gammapy.maps.geom.MapCoords` object or tuple of
            coordinate arrays for each dimension of the map.  Tuple
            should be ordered as (lon, lat, x_0, ..., x_n) where x_i
            are coordinates for non-spatial dimensions of the map.

        interp : {None, 'linear', 'nearest'}
            Interpolate data values. None corresponds to 'nearest',
            but might have advantages in performance, because no
            interpolator is set up.

        Returns
        -------
        vals : `~numpy.ndarray`
           Values of pixels in the flattened map.
           np.nan used to flag coords outside of map

        """
        pass

    @abc.abstractmethod
    def get_by_pix(self, pix, interp=None):
        """Return map values at the given pixel coordinates.

        Parameters
        ----------
        pix : tuple
            Tuple of pixel index arrays for each dimension of the map.
            Tuple should be ordered as (I_lon, I_lat, I_0, ..., I_n)
            for WCS maps and (I_hpx, I_0, ..., I_n) for HEALPix maps.
            Pixel indices can be either float or integer type.  Float
            indices will be rounded to the nearest integer.

        interp : {None, 'linear', 'nearest'}
            Interpolate data values. None corresponds to 'nearest',
            but might have advantages in performance, because no
            interpolator is set up.

        Returns
        ----------
        vals : `~numpy.ndarray`
           Values of pixels in the flattened map
           np.nan used to flag coords outside of map

        """
        pass

    @abc.abstractmethod
    def fill_by_coords(self, coords, weights=None):
        """Fill pixels at the given map coordinates with values in `weights`
        vector.

        Parameters
        ----------
        coords : tuple or `~gammapy.maps.geom.MapCoords`
            `~gammapy.maps.geom.MapCoords` object or tuple of
            coordinate arrays for each dimension of the map.  Tuple
            should be ordered as (lon, lat, x_0, ..., x_n) where x_i
            are coordinates for non-spatial dimensions of the map.

        weights : `~numpy.ndarray`
            Weights vector. If None then a unit weight will be assumed
            for each element in `coords`.
        """
        pass

    @abc.abstractmethod
    def fill_by_pix(self, pix, weights=None):
        """Fill pixels at the given pixel coordinates with values in `weights`
        vector.

        Parameters
        ----------
        pix : tuple
            Tuple of pixel index arrays for each dimension of the map.
            Tuple should be ordered as (I_lon, I_lat, I_0, ..., I_n)
            for WCS maps and (I_hpx, I_0, ..., I_n) for HEALPix maps.
            Pixel indices can be either float or integer type.  Float
            indices will be rounded to the nearest integer.

        weights : `~numpy.ndarray`
            Weights vector. If None then a unit weight will be assumed
            for each element in `pix`.
        """
        pass

    @abc.abstractmethod
    def set_by_coords(self, coords, vals):
        """Set pixels at the given map coordinates to the values in `vals`
        vector.

        Parameters
        ----------
        coords : tuple or `~gammapy.maps.geom.MapCoords`
            `~gammapy.maps.geom.MapCoords` object or tuple of
            coordinate arrays for each dimension of the map.  Tuple
            should be ordered as (lon, lat, x_0, ..., x_n) where x_i
            are coordinates for non-spatial dimensions of the map.

        vals : `~numpy.ndarray`
            Values vector.  Pixels at `coords` will be set to these values.
        """
        pass

    @abc.abstractmethod
    def set_by_pix(self, pix, vals):
        """Set pixels at the given pixel coordinates to the values in `vals`
        vector.

        Parameters
        ----------
        pix : tuple
            Tuple of pixel index arrays for each dimension of the map.
            Tuple should be ordered as (I_lon, I_lat, I_0, ..., I_n)
            for WCS maps and (I_hpx, I_0, ..., I_n) for HEALPix maps.
            Pixel indices can be either float or integer type.  Float
            indices will be rounded to the nearest integer.

        vals : `~numpy.ndarray`
            Values vector. Pixels at `pix` will be set to these values.
        """
        pass
