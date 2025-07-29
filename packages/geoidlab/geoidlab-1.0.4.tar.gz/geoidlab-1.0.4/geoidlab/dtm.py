############################################################
# Utilities for digital terrain modeling                   #
# Copyright (c) 2024, Caleb Kelly                          #
# Author: Caleb Kelly  (2024)                              #
############################################################
import lzma

import numpy as np

from pathlib import Path
from geoidlab import coordinates as co
from geoidlab.legendre import ALF, ALFsGravityAnomaly
from geoidlab.numba.dtm import compute_harmonic_sum
from tqdm import tqdm

from multiprocessing import Pool, cpu_count
from pathlib import Path




class DigitalTerrainModel:
    def __init__(self, model_name=None, nmax=2190, ellipsoid='wgs84') -> None:
        '''
        Initialize the DigitalTerrainModel class
        
        Parameters
        ----------
        model_name : Name of the DTM model file (full path)
        nmax       : Maximum degree of spherical harmonics
        ellipsoid  : Reference ellipsoid

        Returns
        -------
        None
        '''
        self.name = model_name
        self.nmax = nmax
        self.ellipsoid = ellipsoid
        # self.progress = show_progress

        if self.name is None:
            script_dir: Path = Path(__file__).resolve().parent
            self.name = script_dir / 'data' / 'DTM2006.xz'
            print(f'Using compressed DTM2006.0 file in {script_dir}/data ...')
            with lzma.open(self.name, 'rt') as f:
                self.dtm = f.readlines()
        else:
            self.name = Path(self.name)
            try:
                print(f'Reading DTM file {self.name} ...')
                if self.name.suffix == '.xz':
                    with lzma.open(self.name, 'rt') as f:
                        self.dtm = f.readlines()
                else:
                    with open(self.name, 'r') as f:
                        self.dtm = f.readlines() # self.dtm is the DTM2006 text file
            except Exception as e:
                raise Exception(f'Error reading DTM file {self.name}: {str(e)}')
                

    @staticmethod
    def process_chunk(args) -> np.ndarray:
        self, lon_chunk, lat_chunk, height_chunk, nmax, ellipsoid, leg_progress, chunk_idx = args
        _, theta, _ = co.geodetic2spherical(phi=lat_chunk, lambd=lon_chunk, ellipsoid=ellipsoid, height=height_chunk)
        _lambda = np.radians(lon_chunk)
        m = np.arange(nmax + 1)
        mlambda = m[:, np.newaxis] * _lambda
        cosm = np.cos(mlambda)
        sinm = np.sin(mlambda)
        
        Pnm, _ = ALFsGravityAnomaly(vartheta=theta, nmax=nmax, ellipsoid=ellipsoid, show_progress=leg_progress)
        
        # H = 

        return compute_harmonic_sum(Pnm, self.HCnm, self.HSnm, cosm, sinm)

    def read_dtm2006(self) -> None:
        '''
        Read DTM data stored as compressed LZMA file or the original DTM2006 file
        '''
        HCnm = np.zeros((self.nmax + 1, self.nmax + 1))
        HSnm = np.zeros((self.nmax + 1, self.nmax + 1))

        for line in self.dtm:
            line = line.split()

            n = int(line[0])
            m = int(line[1])

            if n > self.nmax:
                break

            if n <= self.nmax + 1 and m <= self.nmax + 1:
                HCnm[n, m] = float(line[2].replace('D', 'E'))
                HSnm[n, m] = float(line[3].replace('D', 'E'))
        self.HCnm = HCnm
        self.HSnm = HSnm
    
    def dtm2006_height_point(
        self,
        lon: float,
        lat: float,
        height=None
    ) -> float:    
        '''
        Compute height for a single point using DTM2006.0 spherical harmonics
        
        Parameters
        ----------
        lon       : geodetic longitude
        lat       : geodetic latitude
        
        Returns
        -------
        H         : synthesized height
        '''
        # Check if self has the HCnm attribute
        if not hasattr(self, 'HCnm') or not hasattr(self, 'HSnm'):
            self.read_dtm2006()
            
        if height is None:
            height = 0
        
        _, theta, _ = co.geodetic2spherical(
            phi=np.array([lat]), 
            lambd=np.array([lon]), 
            ellipsoid=self.ellipsoid,
            height=height
        )
        
        theta = theta[0]
        _lambda = np.radians(lon)
        m = np.arange(self.nmax + 1)[:, np.newaxis]
        mlambda = m * _lambda
        cosm = np.cos(mlambda)
        sinm = np.sin(mlambda)
        
        Pnm, _ = ALF(vartheta=theta, nmax=self.nmax, ellipsoid=self.ellipsoid)
        H = np.sum((self.HCnm * Pnm) @ cosm + (self.HSnm * Pnm) @ sinm)
        
        return float(H)
    
    def dtm2006_height(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        chunk_size: int = 800,
        leg_progress: bool = False,
        height: np.ndarray = None,
        n_workers: int = None,
        save: bool = True
    ) -> np.ndarray:
        '''
        Compute heights from DTM2006.0 spherical harmonic coefficients
        
        Parameters
        ----------
        lon         : geodetic longitude
        lat         : geodetic latitude
        chunk_size  : number of points to process at a time
        leg_progress: show progress bar for Legendre polynomial computation
        height      : height above ellipsoid (optional)
        n_workers   : number of parallel workers
        
        Returns
        -------
        H           : synthesized height
        '''
        lon = np.asarray(lon)
        lat = np.asarray(lat)
        
        if lon.shape != lat.shape:
            raise ValueError('lon and lat must have the same shape')

        input_shape = lon.shape
        lon_flat = lon.ravel()
        lat_flat = lat.ravel()
        height_flat = np.zeros_like(lon_flat) if height is None else height.ravel()
        num_points = len(lon_flat)
        
        # Check if self has the HCnm attribute
        if not hasattr(self, 'HCnm') or not hasattr(self, 'HSnm'):
            self.read_dtm2006()
        
        if num_points == 1:
            return self.dtm2006_height_point(lon_flat[0], lat_flat[0])

        H_flat = np.zeros(num_points)
        
        # Memory-based chunk size cap (optional)
        max_chunk_memory = 4e9  # ~4GB in bytes
        point_memory = (self.nmax + 1) ** 2 * 8
        max_points = int(max_chunk_memory / point_memory)
        chunk_size = min(chunk_size, max_points)
        
        if num_points <= chunk_size:
            r, theta, _ = co.geodetic2spherical(
                phi=lat_flat,
                lambd=lon_flat,
                ellipsoid=self.ellipsoid,
                height=height_flat
            )
            _lambda = np.radians(lon_flat)
            m = np.arange(self.nmax + 1)
            mlambda = m[:, np.newaxis] * _lambda
            cosm = np.cos(mlambda)
            sinm = np.sin(mlambda)
            
            Pnm, _ = ALFsGravityAnomaly(
                vartheta=theta,
                nmax=self.nmax,
                ellipsoid=self.ellipsoid,
                show_progress=leg_progress
            )
            
            H_flat = compute_harmonic_sum(Pnm, self.HCnm, self.HSnm, cosm, sinm)
        else:
            n_workers = n_workers or cpu_count()
            chunk_starts = list(range(0, num_points, chunk_size))
            chunks = [
                (
                    self,
                    lon_flat[start:min(start + chunk_size, num_points)],
                    lat_flat[start:min(start + chunk_size, num_points)],
                    height_flat[start:min(start + chunk_size, num_points)],
                    self.nmax,
                    self.ellipsoid,
                    leg_progress,
                    i  # Chunk index for timing
                )
                for i, start in enumerate(chunk_starts)
            ]
            
            with Pool(processes=n_workers) as pool:
                results = list(tqdm(pool.imap(DigitalTerrainModel.process_chunk, chunks), total=len(chunks), desc='Computing chunks'))
            
            for start, result in zip(chunk_starts, results):
                end = min(start + chunk_size, num_points)
                H_flat[start:end] = result
        
        H = H_flat.reshape(input_shape)
        
        if save:
            DigitalTerrainModel.save_dtm2006_height(lon, lat, H, self.nmax)
            
        return H
    
    # Create a static method that saves writes H as a netcdf files if H is a 2D array
    @staticmethod
    def save_dtm2006_height(
        lon: np.ndarray,
        lat: np.ndarray,
        H: np.ndarray,
        nmax: int,
        filename: str = 'H_dtm2006.nc'
    ) -> None:
        '''
        Save synthesized height to a netCDF file
        
        Parameters
        ----------
        lon       : 2D array of geodetic longitudes
        lat       : 2D array of geodetic latitudes
        H         : 2D array of synthesized heights
        filename  : path to the netCDF file
        '''
        if nmax is None:
            raise ValueError('nmax must be provided')
        
        from netCDF4 import Dataset
        from datetime import datetime, timezone
        
        # Ensure all inputs are 2D arrays with the same shape
        if lon.shape != lat.shape or lon.shape != H.shape:
            raise ValueError('lon, lat, and H must have the same shape')
        
        # Create the output directory if it doesn't exist
        output_dir = Path('outputs')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Update filename to include nmax
        filename = filename.replace('.nc', f'_{nmax}.nc')
        
        # Full file path
        file_path = output_dir / filename
        
        # Extract 1D coordinate arrays from 2D grids (assuming regular grid from np.meshgrid)
        lon_1d = lon[0, :]
        lat_1d = lat[:, 0]
        
        # Create and write to the netCDF file
        with Dataset(file_path, 'w', format='NETCDF4') as ds:
            # --- Global Attributes ---
            ds.title = 'Synthesized Heights from DTM2006.0 Model'
            ds.description = (
                'This dataset contains synthesized heights representing terrain elevations '
                'computed from the DTM2006.0 spherical harmonic model.'
            )
            ds.creation_date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            ds.source = 'DTM2006.0 spherical harmonic coefficients'
            ds.author = 'geoidlab development team'  
            ds.software = 'geoidlab'  
            ds.conventions = 'CF-1.8'  # Optional, aligns with geospatial standards
            
            # --- Dimensions ---
            ds.createDimension('lon', len(lon_1d))
            ds.createDimension('lat', len(lat_1d))
            
            # --- Variables ---
            # Longitude
            lon_var = ds.createVariable('lon', 'f8', ('lon',))
            lon_var.long_name = 'longitude'
            lon_var.units = 'degrees'
            lon_var.standard_name = 'longitude'
            lon_var.description = 'Geodetic longitude of grid points, measured east from Greenwich.'
            
            # Latitude
            lat_var = ds.createVariable('lat', 'f8', ('lat',))
            lat_var.long_name = 'latitude'
            lat_var.units = 'degrees'
            lat_var.standard_name = 'latitude'
            lat_var.description = 'Geodetic latitude of grid points, measured north from the equator.'
            
            # Synthesized Height
            H_var = ds.createVariable('H', 'f8', ('lat', 'lon'))
            H_var.long_name = 'synthesized_height'
            H_var.units = 'meters'
            H_var.standard_name = 'height_above_reference_ellipsoid' 
            H_var.description = (
                'Synthesized terrain height above the reference ellipsoid, computed from '
                'DTM2006.0 spherical harmonic coefficients.'
            )
            H_var.coordinates = 'lon lat'  # Link to coordinate variables
            
            # --- Write Data ---
            lon_var[:] = lon_1d
            lat_var[:] = lat_1d
            H_var[:, :] = H