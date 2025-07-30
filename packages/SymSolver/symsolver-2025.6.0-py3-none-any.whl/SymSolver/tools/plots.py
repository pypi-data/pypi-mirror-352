"""
File Purpose: plots
"""

from .imports import ImportFailed
from .sentinels import NO_VALUE

try:
    import numpy as np
except ImportError as err:
    np = ImportFailed('numpy', err=err)
try:
    import matplotlib.pyplot as plt
    import matplotlib as mpl
except ImportError as err:
    plt = ImportFailed('matplotlib.pyplot', err=err)
    mpl = ImportFailed('matplotlib', err=err)


''' ----------------------------- Plotting ----------------------------- '''

def centered_extent1D(coords, *, L=None, ndim0_ok=False):
    '''returns extent given coords (which should be sorted from min to max, and evenly spaced).
    These are the limits such that the values will line up with pixel centers,
    instead of the left and right edges of the plot.

    if L is provided, ony the first and last values of coords are used, and L is used as the length of the array.

    np.asanyarray(coords).squeeze() must have ndim <= 1. ndim==1 required if not ndim0_ok.
    if ndim0_ok and ndim==0, return np.array([coords - 0.5, coords + 0.5]);
    '''
    coords = np.asanyarray(coords).squeeze()
    assert coords.ndim <= 1
    if ndim0_ok:
        if coords.ndim == 0:
            return np.array([coords[()] - 0.5, coords[()] + 0.5])
    else:
        assert coords.ndim != 0
    if L is None:
        L = len(coords)
    npix = L - 1  # number of pixels across
    dist = (coords[-1] - coords[0])   # full length across
    d = dist / npix  # distance between pixel centers
    # add half a pixel on each end.
    return np.array([*(coords[0] + np.array([0 - d/2, dist + d/2]))])

def centered_extent(xcoords, ycoords, *, Lx=None, Ly=None, shape=None, ndim0_ok=False):
    '''returns extent (to go to imshow), given xcoords, ycoords. Assumes origin='lower'.
    Use this method to properly align extent with middle of pixels.
    (Noticeable when imshowing few enough pixels that individual pixels are visible.)

    This method handles: "Alignment is not centered if just using min & max of coordinate arrays."
        (because e.g. in x, we want center of leftmost pixel to be min(xcoords),
        but if you use extent=(min(xcoords),...) you will get that the _left_ of leftmost pixel is that value.
        so, you need to add half a pixel on each side when determining the proper extent.)
    
    xcoords and ycoords should be arrays.
    (This method uses their first & last values, and their lengths.)
    if Lx and/or Ly are provided, use them as the lengths of coords instead.

    np.asanyarray(coords).squeeze() must have ndim <= 1. ndim==1 required if not ndim0_ok.
    if ndim0_ok and ndim==0, use np.array([coords - 0.5, coords + 0.5]) for those coords.

    returns extent == np.array([left, right, bottom, top]).
    '''
    return np.array([*centered_extent1D(xcoords, L=Lx, ndim0_ok=ndim0_ok),
                     *centered_extent1D(ycoords, L=Ly, ndim0_ok=ndim0_ok)])

def centered_extent_from_extent(extent, shape):
    '''return extent (to go to imshow) given extent & shape, assuming origin='lower'.
    Use this method to properly align extent with middle of pixels.
    '''
    return (*centered_extent1D(extent[:2], L=shape[0]), *centered_extent1D(extent[2:], L=shape[1]))

def get_symlog_ticks(coords, extent, N=5):
    '''returns labels for N ticks given coords.
    Always tries to include one tick for the smallest exponent, and one tick at min and max values.
    '''
    raise NotImplementedError

def evenly_spaced_idx(length, N):
    '''return N evenly spaced indices for a list of the given length.'''
    return np.round(np.linspace(0, length - 1, N)).astype(int)

def colors_from_cmap(cmap, N):
    '''get N evenly spaced colors from the colormap cmap. if cmap is a string, gets matplotlib's default.'''
    if isinstance(cmap, str):
        from matplotlib import cm
        cmap_actual = getattr(cm, cmap)
        return colors_from_cmap(cmap_actual, N)
    return cmap(np.linspace(0, 1, N))

def _colorbar_extent(under=None, over=None):
    '''returns appropriate value for 'extend' in colorbar(extend=..., ...)

    (under provided, over provided) --> value
        True,       True            --> 'both'
        True,       False           --> 'min'
        False,      True            --> 'max'
        False,      False           --> 'neither'
    '''
    lookup = {(True, True): 'both', (True, False): 'min', (False, True): 'max', (False, False): 'neither'}
    return lookup[(under is not None, over is not None)]

def _set_colorbar_extend(cmap):
    '''sets cmap.colorbar_extend appropriately.
    Destructive; cmap will be altered directly (as opposed to returning a new cmap).

    compares cmap(0.0) to cmap.get_under(), and cmap(1.0) to cmap.get_over().
        If unequal, makes triangle at that end.
    E.g. if cmap(0.0) != cmap.get_under(), but cmap(1.0) == cmap.get_over(),
        makes triangle at bottom but not top. extend='min'.

    returns cmap.
    '''
    under_was_set = True if ( not np.array_equal(cmap(0.0), cmap.get_under()) ) else None
    over_was_set  = True if ( not np.array_equal(cmap(1.0), cmap.get_over())  ) else None
    cmap.colorbar_extend = _colorbar_extent(under=under_was_set, over=over_was_set)

def with_colorbar_extend(cmap):
    '''returns a copy of cmap with colorbar_extend set appropriately, based on cmap's extremes.'''
    cmap_c = cmap.copy()
    _set_colorbar_extend(cmap_c)
    return cmap_c

def extended_cmap(cmap=None, under=None, over=None, bad=None, N=None):
    '''creates a cmap with the extremes provided.

    cmap: None, string, colormap, or other iterable
        None --> use the matplotlib default colormap from rc params.
        string --> plt.get_cmap(cmap, N)
            E.g. 'viridis' --> matplotlib.cm.viridis.
        colormap --> use the colormap provided.
        iterable --> use matplotlib.colors.listed_colormap(cmap)
            E.g. ['#FFFFFF00', '#d7d7d7FF'] --> (white with alpha 00/FF) & (gray with alpha FF/FF)
    under, over, bad: None, string, RGB, RGBA, or any other color which matplotlib can understand.
        under: color for points less than vmin.
            A triangle with this color will appear at bottom of colorbar, if under is set.
        over: color for points greater than vmax.
            A triangle with this color will appear at top of colorbar, if over is set.
        bad: color for bad points (NaNs).
            There is no representation of this color on the colorbar;
            be sure to tell viewers the meaning of this color if it appears on the plot.
    N: None or int
        resample cmap to this many points, if cmap is provided via string.
        (If cmap is any other object, ignore this kwarg.)

    returns: the resulting colormap.
    '''
    try:
        cmap0 = plt.get_cmap(cmap, N)
    except ValueError:
        if isinstance(cmap, str):
            raise
        try:
            cmap0 = mpl.colors.ListedColormap(cmap)
        except Exception as err:
            raise err from None
    cmap1 = cmap0.with_extremes(under=under, over=over, bad=bad)
    cmap2 = with_colorbar_extend(cmap1)
    return cmap2

cmap_extended = extended_cmap  # alias

def make_colorbar_axes(location='right', ticks_position=None, ax=None, pad=0.01, size=0.02):
    ''' Creates an axis appropriate for putting a colorbar.

    location: 'right' (default), 'left', 'top', or 'bottom'
        location of colorbar relative to image.
        Note: you will want to set orientation appropriately.
    ticks_position: None (default), 'right', 'left', 'top', or 'bottom'
        None -> ticks are on opposite side of colorbar from image.
        string -> use this value to set ticks position.
    ax: None or axes object
        None -> use plt.gca()
        this is the axes which will inform the size and position for cax.
        it is appropriate to use ax = axes for the image.
    pad: number (default 0.01)
        padding between cax and ax.
        TODO: what does the number really mean?
    size: number (default 0.02)
        size of colorbar.
        TODO: what does the number really mean?

    Adapted from https://stackoverflow.com/a/56900830.
    Returns cax.
    '''
    if ax is None:
        ax = plt.gca()
    p = ax.get_position()
    # calculate cax params.
    ## fig.add_axes(rect) has rect=[x, y, w, h],
    ## where x and y are location for lower left corner of axes.
    ## and w and h are width and height, respectively.
    assert location in ('right', 'left', 'top', 'bottom')
    if location in ('right', 'left'):
        y = p.y0
        h = p.height
        w = size
        if location == 'right':
            x = p.x1 + pad
        else: #'left'
            x = p.x0 - pad
    else: #'top' or 'bottom'
        x = p.x0
        w = p.width
        h = size
        if location == 'top':
            x = p.y1 + pad
        else: #'bottom'
            x = p.y1 - pad

    # make the axes
    cax = plt.gcf().add_axes([x, y, w, h])
    
    # Change ticks position
    if ticks_position is None:
        ticks_position = location
    if ticks_position in ('left', 'right'):
        cax.yaxis.set_ticks_position(ticks_position)
    else: #'top' or 'bottom'
        cax.xaxis.set_ticks_position(ticks_position)

    return cax

make_cax = make_colorbar_axis = make_colorbar_axes  # alias

def colorbar(*args__colorbar, location='right', ticks_position=None, ax=None, pad=0.01, size=0.02,
             sca=False, cax=NO_VALUE, **kw__colorbar):
    '''creates a colorbar via plt.colorbar(...), but uses cax=make_cax(...) unless cax is provided.
    location, ticks_position, ax, pad, and size are passed to make_cax.
    sca: bool, default False.
        whether to set current axes to colorbar axes. True --> plt.gcf() will give colorbar axes afterwards.
    
    *args and additional **kwargs go to plt.colorbar.

    returns result of plt.colorbar
    '''
    if cax is NO_VALUE:
        cax = make_cax(location=location, ticks_position=ticks_position, ax=ax, pad=pad, size=size)
    if not sca: plot_axes = plt.gca()
    result = plt.colorbar(*args__colorbar, cax=cax, **kw__colorbar)
    if not sca: plt.sca(plot_axes)  # "not setting to colorbar axes", i.e. go back to original plot axes.
    return result

class MaintainAxes():
    '''context manager which ensures original axes are restored upon exiting.'''
    def __init__(self):
        pass
    def __enter__(self):
        self.ax = plt.gca()
    def __exit__(self, exc_type, exc_value, traceback):
        plt.sca(self.ax)


MaintainCurrentAxes = MaintainAxes
