import argparse
import sys
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from pathlib import Path
from matplotlib.colors import Colormap
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

from geoidlab.mapping.colormaps import parula_cmap, bright_rainbow_cmap, cpt_cmap
from geoidlab.cli.commands.utils.common import directory_setup

CUSTOM_CMAPS = {
    'parula': parula_cmap(),
    'bright_rainbow': bright_rainbow_cmap()
}

# Unit conversion from meters
UNIT_CONVERSIONS = {
    'cm': 100,
    'mm': 1000
}

cpt_list = cpt_cmap(cpt_list=True)

def get_colormap(cmap_name: str) -> Colormap:
    '''Retrieve colormap by name, handling custom and GMT .cpt colormaps'''
    if cmap_name in CUSTOM_CMAPS:
        return CUSTOM_CMAPS[cmap_name]
    elif cmap_name.endswith('.cpt'):
        return cpt_cmap(cmap_name)
    else:
        try:
            return plt.get_cmap(cmap_name)
        except ValueError:
            raise ValueError(f'Invalid colormap: {cmap_name}. Use --list-cmaps to see available options.')

def list_colormaps() -> None:
    '''Print available colormaps.'''
    print('Available colormaps:')
    print('- Standard Matplotlib colormaps (e.g., viridis, plasma, etc.)')
    print('- Custom colormaps:', ', '.join(CUSTOM_CMAPS.keys()))
    print('- GMT .cpt colormaps:', ', '.join(cpt_list))
    
def nice_scale_length(range_size: float) -> float:
    '''Return a nice scalebar length (e.g., 10, 50, 100) based on range size'''
    candidates = [1, 2, 5, 10, 20, 50, 100, 200, 250]
    target = range_size * 0.2  # 10% of the range
    return min(candidates, key=lambda x: abs(x - target))

def add_north_arrow(ax, x=0.95, y=0.95, size=30, color='black') -> None:
    ax.annotate('N', xy=(x, y), xytext=(0, size),
               arrowprops=dict(arrowstyle='->', color=color),
               xycoords=ax.transAxes, textcoords='offset points',
               ha='center', va='center', fontsize=size//2, 
               fontweight='bold', color=color)
    
def add_plot_arguments(parser) -> None:
    '''Add plotting arguments to an ArgumentParser instance'''
    parser.add_argument('-f', '--filename', type=str, help='NetCDF file to plot')
    parser.add_argument('-v', '--variable', action='append', type=str, help='Variable name(s) to plot')
    parser.add_argument('-c', '--cmap', type=str, help='Colormap to use. For GMT .cpt files, use the file name with extension.', default='viridis')
    parser.add_argument('--fig-size', type=int, nargs=2, default=[5, 5], help='Figure size in inches')
    parser.add_argument('--vmin', type=float, help='Minimum value for colorbar')
    parser.add_argument('--vmax', type=float, help='Maximum value for colorbar')
    parser.add_argument('--font-size', type=int, default=10, help='Font size for labels')
    parser.add_argument('--title-font-size', type=int, default=12, help='Font size for title')
    parser.add_argument('--font-family', type=str, default='Arial', help='Font family for labels')
    parser.add_argument('--list-cmaps', action='store_true', help='List available colormaps and exit')
    parser.add_argument('--save', action='store_true', help='Save figure')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for saving figure')
    parser.add_argument('--proj-name', type=str, default='GeoidProject', help='Name of the project')
    parser.add_argument('--xlim', type=float, nargs=2, default=None, help='X-axis limits')
    parser.add_argument('--ylim', type=float, nargs=2, default=None, help='Y-axis limits')
    parser.add_argument('--scalebar', action='store_true', help='Show scalebar')
    parser.add_argument('--scalebar-units', type=str, default='km', choices=['km', 'degrees'], help='Scalebar units')
    parser.add_argument('--scalebar-fancy', action='store_true', help='Use fancy scalebar')
    parser.add_argument('-u', '--unit', type=str, default=None, choices=['m', 'cm', 'mm'], help='Unit to display data with length units')
    

def main(args=None) -> None:
    if args is None:
        parser = argparse.ArgumentParser(description='Plot a NetCDF file')
        add_plot_arguments(parser)
        args = parser.parse_args()
        
    if getattr(args, 'list_cmaps', False):
        list_colormaps()
        return 0
    
    # if args.list_cmaps:
    #     list_colormaps()
    #     return 0
    
    # Ensure we have a filename
    if not args.filename:
        print('Error: No filename specified. Use -f or --filename to specify a NetCDF file.')
        return 1
    
    directory_setup(args.proj_name)

    plt.rcParams.update({'font.size': args.font_size, 'font.family': args.font_family})
    
    ds = xr.open_dataset(args.filename)
    if args.variable:
        variables = [ds[var] for var in args.variable]
    else:
        variables = list(ds.data_vars.values())
        if not variables:
            raise ValueError('No data variables found in the NetCDF file.')
    
    # Determine subplot grid
    n_vars = len(variables)
    ncols = int(np.ceil(np.sqrt(n_vars)))
    nrows = int(np.ceil(n_vars / ncols))
    
    fig, axes = plt.subplots(nrows, ncols, figsize=(args.fig_size[0] * ncols, args.fig_size[1] * nrows))
    axes = np.atleast_2d(axes)
    
    for i, var in enumerate(variables):
        row, col = divmod(i, ncols)
        ax = axes[row, col]
        lon, lat = var.coords['lon'].values, var.coords['lat'].values
        data = var.values
        
        units = var.attrs.get('units', '')
        
        # Convert units
        if args.unit is not None and args.unit != 'm':
            if units == 'meters' or units == 'm':
                data = data * UNIT_CONVERSIONS[args.unit]
                units = f'{args.unit}'
            
        pcm = ax.pcolormesh(lon, lat, data, cmap=get_colormap(args.cmap), shading='auto', vmin=args.vmin, vmax=args.vmax)
        long_name = var.attrs.get('long_name', var.name)
        ax.set_title(f'{long_name}', fontweight='bold', fontsize=args.title_font_size)
        ax.grid(which='both', linewidth=0.01)
        ax.minorticks_on()
        ax.grid(which='minor', linewidth=0.01)
        ax.set_xlim(args.xlim)
        ax.set_ylim(args.ylim)
        cbar = fig.colorbar(pcm, ax=ax, label=f'{long_name} [{units}]' if units else long_name)
        
        # Add scalebar
        if args.scalebar:
            lon_range = args.xlim if args.xlim else (lon.min(), lon.max())
            scale_length = nice_scale_length(lon_range[1] - lon_range[0])
            if args.scalebar_units == 'km':
                mean_lat = np.mean(lat) if args.ylim is None else np.mean(args.ylim)
                scale_length_km = scale_length * 111.11 * np.cos(np.deg2rad(mean_lat))
                scale_label = f'{int(scale_length_km)} km'
            else:
                scale_label = f'{int(scale_length)} {args.scalebar_units}°'
                
            if args.scalebar_fancy:
                # Create a segmented scalebar with alternating colors
                
                n_segments = 4  # e.g., black, white, black
                segment_length = scale_length / n_segments
                colors = ['black', 'white'] * n_segments
                colors = colors[:n_segments]  # Alternating colors
                scale_bars = []

                # Calculate segment width in axes coordinates (0 to 1)
                lon_range = lon.max() - lon.min()
                segment_width_axes = segment_length / lon_range  # Fraction of x-axis

                for i in range(n_segments):
                    # Create a segment of the scalebar
                    sb = AnchoredSizeBar(
                        ax.transData,
                        segment_length,  # Length in data coordinates (degrees)
                        '',  # Label only on last segment
                        'lower left',  # Position
                        pad=0.35,
                        color=colors[i],
                        frameon=False,  # No frame for segments
                        size_vertical=0.04,  # Thickness
                        fontproperties={'size': 8},
                        alpha=0.25,
                        borderpad=0.5,
                        bbox_to_anchor=(i * segment_width_axes, 0),  # Offset in axes coordinates
                        bbox_transform=ax.transAxes  # Use axes coordinates for positioning
                    )
                    scale_bars.append(sb)
                    ax.add_artist(sb)
                    
                    # Add centered label below the entire scalebar
                    ax.text(
                        0.6 * (n_segments * segment_width_axes),  # Center of scalebar
                        0.035,  # Lower left
                        scale_label,  # Label (e.g., "50°")
                        transform=ax.transAxes,
                        fontsize=8,
                        color='black',
                        ha='center',  # Center horizontally
                        va='top',  # Place below
                        bbox=dict(facecolor='none', edgecolor='none')
                    )
            else:
                sb = AnchoredSizeBar(
                    ax.transData,
                    scale_length,  # Length in data coordinates (degrees)
                    scale_label,  # Label
                    'lower left',  # Position
                    pad=0.35,
                    color='black',
                    frameon=True,  # No frame for segments
                    size_vertical=0.04,  # Thickness
                    fontproperties={'size': 8},
                    alpha=0.25,
                    borderpad=0.5,
                )
                ax.add_artist(sb)
    
    # Hide unused subplots
    for i in range(len(variables), nrows * ncols):
        row, col = divmod(i, ncols)
        ax = axes[row, col]
        ax.set_visible(False)
    
    plt.tight_layout()
    
    if args.save:
        figures_dir = Path(f'{args.proj_name}/results/figures')
        file_name = args.filename.split('/')[-1].split('.')[0]
        plt.savefig(f'{figures_dir}/{file_name}.png', dpi=args.dpi, bbox_inches='tight')
    else:
        plt.show()

if __name__ == '__main__':
    sys.exit(main())
