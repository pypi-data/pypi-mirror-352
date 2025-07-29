############################################################
# Stokes' function and its modifications                   #
# Copyright (c) 2024, Caleb Kelly                          #
# Author: Caleb Kelly  (2024)                              #
############################################################

import numpy as np
import warnings
# from numba import njit

from geoidlab.legendre import legendre_poly_fast
from geoidlab.utils.numba.stokes import stokes_kernel



class Stokes4ResidualGeoid:
    '''
    Class for Stokes' function and its modifications
    '''
    def __init__(
        self,
        lonp, 
        latp, 
        lon, 
        lat,
        psi0=None, 
        nmax=None
    ) -> None:
        '''
        Initialize the Stokes class.
        '''
        self.lonp = np.asarray(lonp)
        self.latp = np.asarray(latp)
        self.lon = np.asarray(lon)
        self.lat = np.asarray(lat)
        self.psi0 = psi0
        self.nmax = nmax
    
    def stokes(self, custom=False, lonp=None, latp=None, lon=None, lat=None) -> tuple:
        '''
        Implements the original Stokes' kernel
        
        Parameters
        ----------
        custom      : flag to use custom custom inputs rather than those in self
        lonp        : longitude of computation point in radians
        latp        : latitude of computation point in radians
        lon         : longitude of integration point in radians
        lat         : latitude of integration point in radians
        
        Returns
        -------
        S_k         : Stokes' kernel
        cos_psi     : cosine of spherical distance from computation point
        '''
        if custom and (lonp is None or latp is None or lon is None or lat is None):
            raise ValueError('lonp, latp, lon, and lat must be provided if custom=True')
            
        if not custom:
            lonp, latp, lon, lat = self.lonp, self.latp, self.lon, self.lat
        else:
            # Ensure that scalar inputs become 1D arrays for correct indexing
            lonp = np.atleast_1d(lonp)
            latp = np.atleast_1d(latp)
            lon = np.atleast_1d(lon)
            lat = np.atleast_1d(lat)
        
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=RuntimeWarning)
            S_k = stokes_kernel(lonp, latp, lon, lat)
        
        return S_k
    
    def wong_and_gore(self) -> np.ndarray:
        '''
        Wong and Gore's modification of Stokes' function, vectorized for performance.
        
        Returns
        -------
        S_wg   : Wong and Gore's modified Stokes' function
        '''
        S, cos_psi = self.stokes()
        
        # Compute Legendre polynomials for all points at once
        Pn_all = legendre_poly_fast(t=cos_psi, nmax=self.nmax)
        # Coefficients for the sum term
        coefficients = np.array([(2 * n + 1) / (n - 1) for n in range(2, self.nmax + 1)])
        # Compute the sum term vectorized across all points
        sum_term = np.dot(Pn_all[:, 2:], coefficients)
        
        # Apply the modification
        S_wg = S - sum_term
        
        return S_wg
    
    def heck_and_gruninger(self) -> np.ndarray:
        '''
        Heck and Gruninger's modification of Stokes' function
        
        Returns
        -------
        S_hg   : Heck and Gruninger's modified Stokes' function
        '''
        S_wg = self.wong_and_gore()
        
        # Stokes' function for a spherical cap (psi_0)
        S_0, cos_psi_0 = self.stokes(lonp=0, latp=0, lon=0, lat=self.psi0, custom=True)
        
        # Wong and Gore for spherical cap (psi_0)
        Pn = legendre_poly_fast(t=cos_psi_0, nmax=self.nmax)
        # Dot product approach for performance
        coefficients = np.array([(2 * n + 1) / (n - 1) for n in range(2, self.nmax + 1)])
        S_wgL = np.dot(Pn[2:], coefficients) 
        # try:
        #     # Dot product approach for performance
        #     coefficients = np.array([(2 * n + 1) / (n - 1) for n in range(2, self.nmax + 1)])
        #     S_wgL = np.dot(Pn[2:], coefficients) 
        # except MemoryError:
        #     S_wgL = 0
        #     for n in range(2, self.nmax + 1):
        #         S_wgL += (2 * n + 1) / (n - 1) * Pn[n]
        
        # Heck and Gruninger
        S_hg = S_wg - (S_0 - S_wgL)
        
        return S_hg
    
    def meissl(self) -> np.ndarray:
        '''
        Meissl's modification of Stokes' function
        
        Returns
        -------
        S_m    : Meissl's modified Stokes' function

        '''
        S, _ = self.stokes()
        S_0, _ = self.stokes(lonp=0, latp=0, lon=0, lat=self.psi0, custom=True)
        
        return S - S_0