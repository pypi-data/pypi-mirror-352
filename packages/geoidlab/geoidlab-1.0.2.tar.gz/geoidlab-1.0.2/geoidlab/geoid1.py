############################################################
# Utilities for geoid modelling                            #
# Copyright (c) 2024, Caleb Kelly                          #
# Author: Caleb Kelly  (2024)                              #
############################################################
import numpy as np
import xarray as xr
# import warnings
# import bottleneck as bn
# from numba import jit, njit

from geoidlab.utils.distances import haversine_fast
from geoidlab.gravity import normal_gravity_somigliana
from geoidlab.constants import earth
from geoidlab.stokes_func1 import Stokes4ResidualGeoid

from tqdm import tqdm

class ResidualGeoid:
    '''
    Geoid class for modeling the geoid via the remove-compute-restore method.
    '''

    VALID_METHODS = {'hg', 'wg', 'og', 'ml'}
    VALID_WINDOW_MODES = {'small', 'cap'}
    VALID_ELLIPSOIDS = {'wgs84', 'grs80'}

    
    def __init__(
        self,
        res_anomaly: xr.Dataset,
        sph_cap: float = 1.0,
        sub_grid: tuple[float, float, float, float] = None,
        method: str = 'hg',
        ellipsoid: str = 'wgs84',
        nmax: int = None,
        window_mode: str = 'small',
        overwrite: bool = True
    ) -> None:
        '''
        Initialize the ResidualGeoid class.

        Parameters
        ----------
        res_anomaly : xr.Dataset
            Gridded residual gravity anomalies.
        sph_cap : float, optional
            Spherical cap for integration, in degrees. Default is 1.0.
        sub_grid : tuple of float, optional
            Sub-grid for integration in the form (min_lon, max_lon, min_lat, max_lat). Required.
        method : str, optional
            Method for integration. Options are 'hg', 'wg', 'og', 'ml'. Default is 'hg'.
        ellipsoid : str, optional
            Reference ellipsoid for normal gravity calculation. Options are 'wgs84', 'grs80'. Default is 'wgs84'.
        nmax : int, optional
            Maximum degree of spherical harmonic expansion. Required for 'hg' and 'wg' methods.
        window_mode : str, optional
            Window mode for integration. Options are 'small' or 'cap'. Default is 'small'.
        overwrite : bool, optional
            Whether to overwrite existing data files. Default is True.

        Raises
        ------
        ValueError
            If any of the input parameters are invalid.

        Returns
        -------
        None
        '''
        window_mode = window_mode.lower()
        if window_mode not in self.VALID_WINDOW_MODES:
            raise ValueError(f'Invalid window_mode: {window_mode}. Must be one of {sorted(self.VALID_WINDOW_MODES)}')
        
        if sub_grid is None or not isinstance(sub_grid, (tuple, list)) or len(sub_grid) != 4:
            raise ValueError('sub_grid must be a tuple/list of 4 values: (min_lon, max_lon, min_lat, max_lat)')
        min_lon, max_lon, min_lat, max_lat = sub_grid
        if not all(isinstance(x, (int, float)) for x in sub_grid):
            raise ValueError('All sub_grid values must be numeric')
        if min_lon >= max_lon or min_lat >= max_lat:
            raise ValueError(f'Invalid sub_grid: min_lon ({min_lon}) < max_lon ({max_lon}), min_lat ({min_lat}) < max_lat ({max_lat})')
            
        method = method.lower()
        if method not in self.VALID_METHODS:
            raise ValueError(f'Invalid method: {method}. Must be one of {sorted(self.VALID_METHODS)}')
            
        if method in {'hg', 'wg'} and (nmax is None or not isinstance(nmax, int) or nmax <= 0):
            raise ValueError(f'nmax must be a positive integer for method {method}, got {nmax}')
        
        if ellipsoid.lower() not in self.VALID_ELLIPSOIDS:
            raise ValueError(f'Invalid ellipsoid: {ellipsoid}. Supported ellipsoids: {sorted(self.VALID_ELLIPSOIDS)}')
        
        if not isinstance(res_anomaly, xr.Dataset) or 'Dg' not in res_anomaly.data_vars or 'lon' not in res_anomaly.coords or 'lat' not in res_anomaly.coords:
            raise ValueError('res_anomaly must be an xarray Dataset with \'Dg\', \'lon\', and \'lat\'')
        
        lon_min, lon_max = res_anomaly['lon'].min().item(), res_anomaly['lon'].max().item()
        lat_min, lat_max = res_anomaly['lat'].min().item(), res_anomaly['lat'].max().item()
        if (min_lon < lon_min or max_lon > lon_max or min_lat < lat_min or max_lat > lat_max):
            raise ValueError(f'sub_grid {sub_grid} is outside res_anomaly bounds (lon: [{lon_min}, {lon_max}], lat: [{lat_min}, {lat_max}])')
        
        self.sub_grid = tuple(float(x) for x in sub_grid)
        self.res_anomaly = res_anomaly
        self.sph_cap = np.float64(sph_cap)
        self.method = method
        self.ellipsoid = ellipsoid.lower()
        self.nmax = int(nmax) if nmax is not None else None
        self.window_mode = window_mode
        
        lon = res_anomaly.lon.values.astype(np.float64)
        lat = res_anomaly.lat.values.astype(np.float64)
        self.nrows, self.ncols = self.res_anomaly['Dg'].shape
        self.dlam = np.float64((max(lon) - min(lon)) / (self.ncols - 1))
        self.dphi = np.float64((max(lat) - min(lat)) / (self.nrows - 1))
        
        self.res_anomaly_P = self.res_anomaly.sel(
            lon=slice(self.sub_grid[0], self.sub_grid[1]), 
            lat=slice(self.sub_grid[2], self.sub_grid[3])
        )
        
        lon_p = self.res_anomaly_P['lon'].values.astype(np.float64)
        lat_p = self.res_anomaly_P['lat'].values.astype(np.float64)
        self.LonP, self.LatP = np.meshgrid(lon_p, lat_p)
        
        self.gamma_0 = normal_gravity_somigliana(phi=self.LatP, ellipsoid=self.ellipsoid)
        self.gamma_0 = (self.gamma_0 * 1e5).astype(np.float64)  # Convert to mGal
        
        lon_full = self.res_anomaly['lon'].values.astype(np.float64)
        lat_full = self.res_anomaly['lat'].values.astype(np.float64)
        self.Lon, self.Lat = np.meshgrid(lon_full, lat_full)
        
        self.R = np.float64(earth()['radius'])
        self.k = (1 / (4 * np.pi * self.gamma_0 * self.R)).astype(np.float64)
        
        self.nrows_P, self.ncols_P = self.res_anomaly_P['Dg'].shape
        if self.window_mode == 'small':
            # self.dn = int(np.round((lon_max - lon_min - (self.sub_grid[1] - self.sub_grid[0])) / self.dlam)) + 1
            # self.dm = int(np.round((lat_max - lat_min - (self.sub_grid[3] - self.sub_grid[2])) / self.dphi)) + 1
            self.dn = int(np.round((self.ncols - self.ncols_P) + 1))  # Longitude points
            self.dm = int(np.round((self.nrows - self.nrows_P) + 1))  # Latitude points
        else:
            self.dn = min(int(np.ceil(self.sph_cap / self.dlam)) * 2 + 1, self.ncols)
            self.dm = min(int(np.ceil(self.sph_cap / self.dphi)) * 2 + 1, self.nrows)
        
        self.N_inner = np.zeros((self.nrows_P, self.ncols_P), dtype=np.float64)
        self.N_far = np.zeros_like(self.N_inner)
        self._smallDg = np.empty((self.dm, self.dn), dtype=np.float64)
        self._smallphi = np.empty_like(self._smallDg)
        self._smalllon = np.empty_like(self._smallDg)
        self._A_k = np.empty_like(self._smallDg)
        self._lat1 = np.empty_like(self._smallDg)
        self._lat2 = np.empty_like(self._smallDg)
        self._lon1 = np.empty_like(self._smallDg)
        self._lon2 = np.empty_like(self._smallDg)

    def _get_window_indices(self, i: int, j: int, lat_p: float, lon_p: float, lat0: float, lon0: float, nrows: int, ncols: int, dm: int, dn: int, dphi: float, dlam: float) -> tuple:
        """
        Compute window indices for a given computation point.

        Parameters
        ----------
        i, j : int
            Indices of the computation point.
        lat_p, lon_p : float
            Latitude and longitude of the computation point.
        lat0, lon0 : float
            Starting latitude and longitude of the grid.
        nrows, ncols : int
            Number of rows and columns in the grid.
        dm, dn : int
            Window dimensions.
        dphi, dlam : float
            Grid spacing in latitude and longitude.

        Returns
        -------
        tuple
            Indices defining the start and end of the window.
        """
        """Compute window indices for given computation point."""
        i_center = int(np.round((lat_p - lat0) / dphi))
        j_center = int(np.round((lon_p - lon0) / dlam))
        i_start = max(0, i_center - dm // 2)
        i_end = min(nrows, i_start + dm)
        j_start = max(0, j_center - dn // 2)
        j_end = min(ncols, j_start + dn)
        i_start = max(0, i_end - dm)
        j_start = max(0, j_end - dn)
        return i_start, i_end, j_start, j_end
    
    
    def get_window(self, i: int, j: int) -> None:
        '''
        Compute windowed data based on window mode ('small' or 'cap').

        Parameters
        ----------
        i, j : int
            Indices of the computation point.

        Returns
        -------
        None
        Compute windowed data based on window mode ('small' or 'cap')
        '''
        i_start, i_end, j_start, j_end = self._get_window_indices(
            i, j, self.LatP[i, j], self.LonP[i, j],
            self.res_anomaly['lat'].values[0], self.res_anomaly['lon'].values[0],
            self.nrows, self.ncols, self.dm, self.dn, self.dphi, self.dlam
        )
        
        window_Dg = self.res_anomaly['Dg'].values[i_start:i_end, j_start:j_end]
        window_phi = np.radians(self.Lat[i_start:i_end, j_start:j_end])
        window_lon = np.radians(self.Lon[i_start:i_end, j_start:j_end])
        if window_Dg.shape != (self.dm, self.dn):
            di, dj = window_Dg.shape
            pad_width = ((0, self.dm - di), (0, self.dn - dj))
            window_Dg = np.pad(window_Dg, pad_width, mode='constant', constant_values=np.nan)
            window_phi = np.pad(window_phi, pad_width, mode='constant', constant_values=np.nan)
            window_lon = np.pad(window_lon, pad_width, mode='constant', constant_values=np.nan)
        np.copyto(self._smallDg, window_Dg)
        np.copyto(self._smallphi, window_phi)
        np.copyto(self._smalllon, window_lon)
    
    def compute_geoid(self) -> np.ndarray:
        '''
        Compute the residual geoid height.

        Returns
        -------
        np.ndarray
            Computed residual geoid heights.
        Compute the residual geoid height
        '''
        phip = np.radians(self.LatP)
        lonp = np.radians(self.LonP)
        cosphip = np.cos(phip)
        
        # Near zone computation
        # Near zone (matches MATLAB with 1/sqrt(pi) factor)
        self.N_inner = self.R / self.gamma_0 * np.sqrt(
            cosphip * np.radians(self.dphi) * np.radians(self.dlam) / np.pi
        ) * self.res_anomaly_P['Dg'].values
        
        psi0 = np.radians(self.sph_cap)
        
        # Precompute all windows and coordinates
        smallDg = np.full((self.nrows_P, self.ncols_P, self.dm, self.dn), np.nan, dtype=np.float64)
        smallphi = np.full_like(smallDg, np.nan)
        smalllon = np.full_like(smallDg, np.nan)
        for i in range(self.nrows_P):
            for j in range(self.ncols_P):
                self.get_window(i, j)
                smallDg[i, j] = self._smallDg
                smallphi[i, j] = self._smallphi
                smalllon[i, j] = self._smalllon
        
        # Validate shapes
        n_points = self.nrows_P * self.ncols_P
        n_window = self.dm * self.dn
        if smalllon.shape != (self.nrows_P, self.ncols_P, self.dm, self.dn):
            raise ValueError(f"smalllon shape {smalllon.shape} does not match expected ({self.nrows_P}, {self.ncols_P}, {self.dm}, {self.dn})")
        
        # Surface area
        lat1 = smallphi - np.radians(self.dphi) / 2
        lat2 = smallphi + np.radians(self.dphi) / 2
        lon1 = smalllon - np.radians(self.dlam) / 2
        lon2 = smalllon + np.radians(self.dlam) / 2
        A_k = self.R**2 * np.abs(lon2 - lon1) * np.abs(np.sin(lat2) - np.sin(lat1))

        S_k_all = np.empty((n_points, n_window), dtype=np.float64)
        # Loop over each computation point with progress reporting.
        for p in tqdm(range(n_points), desc="Computing Stokes' integral"):
            # Extract current point’s data from the precomputed windows
            lonp_pt = lonp.ravel()[p:p+1]
            latp_pt = phip.ravel()[p:p+1]
            # Extract the window for this point (shape: (1, n_window))
            lon_win = smalllon.reshape(n_points, n_window)[p:p+1]
            lat_win = smallphi.reshape(n_points, n_window)[p:p+1]
            # Create a temporary Stokes calculator for this window.
            stokes_calc = Stokes4ResidualGeoid(
                lonp=lonp_pt, latp=latp_pt,
                lon=lon_win, lat=lat_win,
                psi0=psi0, nmax=self.nmax
            )
            # Call the appropriate method on the single point.
            method_map = {
                'og': lambda: stokes_calc.stokes()[0],
                'wg': lambda: stokes_calc.wong_and_gore(),
                'hg': lambda: stokes_calc.heck_and_gruninger(),
                'ml': lambda: stokes_calc.meissl()
            }
            # func = method_map[self.method]
            # S_val = func()
            S_val = method_map[self.method]()
            # For 'og', extract just the Stokes' function.
            if self.method == 'og':
                S_val = S_val[0]
            # S_val should be of shape (1, n_window); save into our vector.
            S_k_all[p, :] = S_val.reshape(1, n_window)
        
        # Reshape S_k_all back to the 4-D array.
        S_k = S_k_all.reshape(self.nrows_P, self.ncols_P, self.dm, self.dn)
        
        # Spherical distance
        sd = haversine_fast(
            lonp[:, :, np.newaxis, np.newaxis],
            phip[:, :, np.newaxis, np.newaxis],
            smalllon, 
            smallphi, 
            in_unit='rad', 
            out_unit='deg'
        )
        sd[sd > self.sph_cap] = np.nan
        S_k[np.isnan(sd)] = np.nan
        
        # Far zone contribution
        self.N_far = np.nansum(A_k * S_k * smallDg, axis=(2, 3)) * self.k
        # temp = bn.nansum(A_k * S_k * smallDg, axis=3)
        # self.N_far = bn.nansum(temp, axis=2) * self.k
        
        # Residual geoid
        N_res = self.N_inner + self.N_far
        return N_res
