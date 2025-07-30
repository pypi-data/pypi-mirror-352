"""
File Purpose: display / print / view objects

[TODO][FIX] viewdict doesn't display properly for very large dicts(?)
"""

import collections
import numbers  # << builtin numbers module
import pydoc
import time
import warnings

from .imports import ImportFailed

try:
    import IPython.display as ipd
except ImportError as err:
    ipd = ImportFailed('IPython.display', err=err)
try:
    import numpy as np
except ImportError as err:
    np = ImportFailed('numpy', err=err)
try:
    import xarray as xr
except ImportError as err:
    xr = ImportFailed('xarray', err=err)

from ..errors import (
    InputConflictError, CatchableNotImplementedError,
    warn_Timeout,
)
from ..defaults import DEFAULTS, ZERO, OnOffSwitch


''' --------------------- View --------------------- '''

class _ViewRateLimiter():
    '''Helps with limiting number of times view() works per second.
    It is helpful to limit view rate in case of bug with recursion and view().
    '''
    def __init__(self):
        self.max_rate = DEFAULTS.TIMEOUT_MAX_VIEW_PER_SECOND
        self.calltimes = collections.deque(maxlen=self.max_rate)
        self._too_soon_start_time = None

    def called__too_soon(self):
        '''things to do when view is called; then returns whether it is too soon.'''
        # update rate, if necessary:
        value_from_defaults = DEFAULTS.TIMEOUT_MAX_VIEW_PER_SECOND
        if self.max_rate != value_from_defaults:
            self.max_rate = value_from_defaults
            self.calltimes = collections.deque(self.calltimes, maxlen=self.max_rate)
        # check if time too soon:
        tcall, tdiff = self.tnow_and_tdiff()
        if len(self.calltimes) < self.calltimes.maxlen:
            too_soon = False
        else:
            too_soon = (tdiff is not None) and (tdiff < 1)  # 1 <--> 1 second
        if too_soon:
            if self._too_soon_start_time is None:
                self._too_soon_start_time = tcall
            str_t_start = time.ctime(self._too_soon_start_time)
            errmsg = (f'Too many view() calls per second (starting at time = {repr(str_t_start)}).\n'
                      f'Using print() until rate decreases to fewer than {self.max_rate} calls per second.\n'
                      f'(Max rate set by DEFAULTS.TIMEOUT_MAX_VIEW_PER_SECOND.)')
            warn_Timeout(errmsg)
        else:
            self._too_soon_start_time = None
        # put calltime into self.calltimes
        self.calltimes.append(tcall)
        # return whether time too soon
        return too_soon

    def tnow_and_tdiff(self):
        '''returns time now and time since earliest-call remembered in self (both in [seconds]).'''
        tnow = time.time()
        tdiff = (tnow - (self.calltimes[0])) if (len(self.calltimes) > 0) else None
        return tnow, tdiff

    def __repr__(self):
        timestr = f'now - ealiest_remembered_call = {self.tnow_and_tdiff()[1]}'
        return f'{type(self).__name__}(max_rate={self.max_rate}, {timestr})'

ViewRateLimiter = _ViewRateLimiter()


def view(x, *args__str, mode=None, **kw__str):
    '''view x as fancy math string.
    x can be any object as long as repr(x) converts it to math string.
    if x is a string, use x instead of repr(x)

    might print() instead of view() if:
        len(x as string) > DEFAULTS.RENDER_MAXLEN, or
        calling view too many times too quickly
            (i.e. more than DEFAULTS.TIMEOUT_MAX_VIEW_PER_SECOND within 1 second), or
        [TODO] ipython display not available.

    mode: None, 'print', 'math', or 'latex'.
        how to view. None --> use DEFAULTS.RENDER_MODE
        print --> always print()
        math --> ipython.display.Math
        latex --> ipython.display.Latex
    '''
    if not isinstance(x, str):
        x = _str(x, *args__str, **kw__str)
    if DEFAULTS.RENDER_MATH:
        if mode is None:
            mode = DEFAULTS.RENDER_MODE
        if mode == 'print':
            pass  # handled below..
        elif len(x) > DEFAULTS.RENDER_MAXLEN:
            # string is too large; don't render as math.
            warnmsg_large_str = ('String at <{}> too large to render as math. '
                                 '(Got {} chars; limit is {}.) (To increase the limit, '
                                 'set DEFAULTS.RENDER_MAXLEN to a larger value.)').format(
                                 hex(id(x)), len(x), DEFAULTS.RENDER_MAXLEN)
            warnings.warn(warnmsg_large_str)
        elif not ViewRateLimiter.called__too_soon():
            # render as math
            if mode == 'math':
                ipd.display(ipd.Math(x))
            elif mode == 'latex':
                ipd.display(ipd.Latex(x))
            else:
                raise ValueError(f'Unknown mode: {repr(mode)}')
            return
    # else
    print(x)


''' --------------------- viewlist, viewdict --------------------- '''

class Viewable():
    '''object with view method and _ipython_display_ method that calls self.view().
    view contents will be determined by self.__str__().
    '''
    def view(self, *args__str, **kw__str):
        '''does view(self)'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return view(self, *args__str, **kw__str)

    def _ipython_display_(self):
        return self.view()


class ViewableSortable(Viewable):
    '''Viewable which is also iterable. provides _view_sorted() and _view_contents().
    set self._view_sortkey to adjust sorting behavior.
    view_sortkey: None, bool, or function of a single arg
        None --> use self._view_sortkey.
                default False for base class, but subclasses may overwrite.
        function --> sorted(self._view_contents(), key=self._view_sortkey)
        True --> sorted(self._view_contents(), key=self._view_sortkey_default)
                default _view_sortkey_default is None (i.e. no key; sort like a list)
        False --> don't sort.
    '''
    _view_sortkey = False
    _view_sortkey_default = None

    def _view_contents(self):
        raise NotImplementedError(f'{type(self)}._view_contents()')

    @classmethod
    def with_view_sortkey(cls, *args, key, **kw):
        '''create new instance of cls with result._view_sortkey = sortkey'''
        result = cls(*args, **kw)
        result._view_sortkey = key
        return result

    def _view_sorted(self):
        '''returns self._view_contents() possibly sorted, depending on self._view_sortkey.
        self._view_sortkey: bool, or function of a single arg
            function --> sorted(self._view_contents(), key=self._view_sortkey)
            True --> sorted(self._view_contents(), key=self._view_sortkey_default)
                    default _view_sortkey_default is None (i.e. no key; sort like a list)
            False --> don't sort.
        '''
        sortkey = getattr(self, '_view_sortkey', False)
        contents = tuple(self._view_contents())
        if callable(sortkey):
            return sorted(contents, key=sortkey)
        elif sortkey:
            key = getattr(self, '_view_sortkey_default', None)
            return sorted(contents, key=key)
        else:
            return contents

    def _view_sortkey(self, term):
        '''returns str(term), i.e. the default sorting is to sort by string representation.'''
        return str(term)


class viewlist(ViewableSortable, list):
    '''list, but _ipython_display_ leads to pretty view.
    Also __str__ is "pretty"-ish, getting __str__ of contents instead of __repr__.
    '''
    def _view_contents(self):
        return self

    def __str__(self):
        contents = ', '.join([str(x) for x in self._view_sorted()])
        return fr'\Big[ {contents} \Big]'

    def __getitem__(self, i):
        '''returns self[i] but as type(self) if i is not an integer'''
        result = super().__getitem__(i)
        return result if isinstance(i, int) else type(self)(result)


class viewtuple(ViewableSortable, tuple):
    '''tuple, but _ipython_display_ leads to pretty view.
    Also __str__ is "pretty"-ish, getting __str__ of contents instead of __repr__.
    '''
    def _view_contents(self):
        return self

    def __str__(self):
        contents = ', '.join([str(x) for x in self._view_sorted()])
        return fr'\Big( {contents} \Big)'

    def __getitem__(self, i):
        '''returns self[i] but as type(self) if i is not an integer'''
        result = super().__getitem__(i)
        return result if isinstance(i, int) else type(self)(result)


class viewdict(ViewableSortable, dict):
    '''dict, but _ipython_display_ leads to pretty view.
    Also __str__ is "pretty"-ish, getting __str__ of values instead of __repr__.
    '''
    # if _view_sortkey = True, use this key to sort:
    _view_sortkey_default = staticmethod(lambda item: item[0])

    def _view_contents(self):
        return self.items()

    def __str__(self):
        kvstr = ((k, str(v)) for k, v in self._view_sorted())
        kvstr = ((k, (v if len(v)<20 else fr'{v} \\')) for k, v in kvstr)  # newline for long strings.
        contents = r' \ \Big| \ '.join([fr'\text{{{k}}}: {v}' for k, v in kvstr])
        return r'\Big\{' + f'{contents}' + r'\Big\}'


def view_after_message(message, obj):
    r'''view('\text{message}'+_str(obj))'''
    view(fr'\text{{{message}}}{_str(obj)}')


''' --------------------- str --------------------- '''

def _str(x, *args, **kw):
    '''str, applying args and kwargs if possible,
    also applying prettification of floats and numpy arrays.
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    try:
        return _str_nonsymbolic(x, *args, **kw)
    except CatchableNotImplementedError:
        pass  # just means we don't know how to do _str_nonsymbolic for x.
    try:
        return x.__str__(*args, **kw)
    except TypeError:
        return x.__str__()

def _str_nonsymbolic(x, *args, numbers_precision=None,
                     array_precision=None, array_annotate=None, array_nanmean=None, array_smallsize=None,
                     **kw):
    '''string for non-SymbolicObject x, intended to be displayed when str(x) appears in a SymbolicObject's string.
    E.g. for str(Product(2, y, 8.1234567)), will call _str_nonsymbolic(2) and _str_nonsymbolic(8.1234567).
    For now, just returns _str(x, *args, **kw).
    [TODO] Eventually, ensure this is woven throughout SymSolver, and make pretty options for floats, numpy arrays, etc.
    '''
    if isinstance(x, numbers.Real):
        return _smallstr_real(x, *args, precision=numbers_precision, **kw)
    elif isinstance(x, numbers.Complex):
        return _smallstr_complex(x, *args, precision=numbers_precision, **kw)
    elif ((not isinstance(np, ImportFailed)) and isinstance(x, np.ndarray)) \
        or ((not isinstance(xr, ImportFailed)) and isinstance(x, xr.DataArray)):
        if x.dtype != np.dtype(object):
            kw_str_arr = dict(precision=array_precision, annotate=array_annotate,
                              nanmean=array_nanmean, smallsize=array_smallsize)
            return _smallstr_array(x, *args, **kw_str_arr, **kw)
    errmsg = f'_str_nonsymbolic(x) for type(x)={type(x).__name__}.'
    raise CatchableNotImplementedError(errmsg)

def _smallstr_real(x, *args__None, precision=None, **kw__None):
    '''small string for real number x that is pretty to look at.
    precision: None or int
        number of sigfigs to show, as per the 'g' format specifier.
        None --> use DEFAULTS.STRINGREP_NUMBERS_PRECISION
    '''
    if precision is None: precision = DEFAULTS.STRINGREP_NUMBERS_PRECISION
    fmt = f'.{precision}g'
    s = format(x, fmt)
    if 'e' in s:  # exponent --> use 'times' & 10^exp.
        base, exp = s.split('e')
        esign, eval_ = exp[0], exp[1:]
        assert esign in ('+', '-'), f"unexpected sign for exponent: {repr(esign)}"
        ssign = '' if esign == '+' else '-'
        seval = eval_.lstrip('0')
        return fr'{base} \times 10^{{{ssign}{seval}}}'
    else:
        return s

def _smallstr_complex(x, *args, precision=None, **kw):
    '''small string for complex number x that is pretty to look at.
    precision: None or int
        number of signfigs to show, as per the 'g' format specifier.
        None --> use DEFAULTS.STRINGREP_NUMBERS_PRECISION
    [TODO] option to use j or i for imaginary unit. (now, always uses j.)
    '''
    real, imag = x.real, x.imag
    real_is_0 = (real == ZERO)
    imag_is_0 = (imag == ZERO)
    realstr = _smallstr_real(real, *args, precision=precision, **kw)
    if imag_is_0:  # looks like a real number to me!
        return realstr
    imagstr = _smallstr_real(imag, *args, precision=precision, **kw)
    if real_is_0:
        return f'{imagstr} j'
    sign = '' if imagstr.startswith('-') else '+ '
    return f'{realstr} {sign}{imagstr} j'

def _smallstr_array(x, *args, precision=None, annotate=None, nanmean=None, smallsize=None, **kw__None):
    '''small string for numerical array x that is pretty to look at. (numerical <--> not dtype object)
    Usually shows the array min, mean, max, & shape.
    If shape <= smallsize, show all array elements instead.
    If 0d array (e.g. np.array(7)) show x[()] (e.g. 7) instead.

    precision: None or int
        number of sigfigs to show for each number, as per the 'g' format specifier.
        None --> use DEFAULTS.STRINGREP_ARRAY_PRECISION.
    annotate: None or bool
        whether to put the words 'min', 'mean', 'max', 'shape' into the result.
        Either way, result will look like a matrix with min & mean in row 1, max & shape in row 2.
        None --> use DEFAULTS.STRINGREP_ARRAY_ANNOTATE.
    nanmean: None or bool
        whether to use 'nan' funcs for array states.
        None --> use DEFAULTS.STRINGREP_ARRAY_NANMEAN.
        True --> use np.nanmin, np.nanmean, np.nanmax.
        False --> use np.min, np.mean, np.max.
    smallsize: None or int
        if x.size <= smallsize, show all array elements instead of the array min, mean, max, & shape.
        None --> use DEFAULTS.STRINGREP_ARRAY_SMALLSIZE.
    '''
    # bookkeeping / startup
    x = np.asanyarray(x)
    if precision is None: precision = DEFAULTS.STRINGREP_ARRAY_PRECISION
    if smallsize is None: smallsize = DEFAULTS.STRINGREP_ARRAY_SMALLSIZE
    if annotate is None: annotate = DEFAULTS.STRINGREP_ARRAY_ANNOTATE
    if nanmean is None: nanmean = DEFAULTS.STRINGREP_ARRAY_NANMEAN
    # check if smallsize or ndim 0
    if x.ndim == 0:
        return _str_nonsymbolic(x[()])
    if x.size <= smallsize:
        content = r',\ '.join(_str_nonsymbolic(elem) for elem in x)
        return fr'\Big[ {content} \Big]'
    # array stats
    min_ = (np.nanmin if nanmean else np.min)(x)
    max_ = (np.nanmax if nanmean else np.max)(x)
    mean = (np.nanmean if nanmean else np.mean)(x)
    # strings setup
    smin_ = _str_nonsymbolic(min_, numbers_precision=precision)
    smax_ = _str_nonsymbolic(max_, numbers_precision=precision)
    smean = _str_nonsymbolic(mean, numbers_precision=precision)
    sshape = str(x.shape)
    annotate_min_ = r'\text{(min) } ' if annotate else ''
    annotate_max_ = r'\text{(max) } ' if annotate else ''
    annotate_mean = r'\text{(mean) } ' if annotate else ''
    annotate_shape = r'\text{shape=}' if annotate else ''
    # result setup
    content = (fr'{annotate_min_}{smin_} & {annotate_mean}{smean} \\ '
               fr'{annotate_max_}{smax_} & {annotate_shape}{sshape}')
    wraps = (r'\left[ \begin{matrix}', r'\end{matrix} \right]')
    result = f'{wraps[0]} {content} {wraps[1]}'
    return result


''' --------------------- repr --------------------- '''

def _repr(x, *args, **kw):
    '''repr, applying args and kwargs if possible'''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    try:
        return x.__repr__(*args, **kw)
    except TypeError:
        return x.__repr__()

def short_repr(x, n=200):
    '''if repr(x) is longer than n characters, return object.__repr__(x) instead.'''
    result = repr(x)
    if (x.__repr__ == object.__repr__) or len(result) <= n:
        return result
    else:
        return object.__repr__(x)


''' --------------------- Conditional display --------------------- '''

def lightweight_maybe_viewer(on=False):
    '''either returns function print_and_view (if `on`), or function do_nothing (if not `on`).
    This is a lightweight version of the MaybeViewer class.

    print_and_view(*args, view=None, format=[], **kw)
        prints args, then does display.view(view).
        if 0 args, print nothing.
        if 1 arg, print(args[0].format(*format), **kw)   # if format is [], skip formatting.
        if >=2 args, print(*args, **kw)   # and note, format is not allowed in this case.

    do_nothing(*args, **kw)
        accepts all args and kwargs, then does nothing.

    if converting objects to strings is non-trivial, you can pass them in to the `format` kwarg,
    so that they are only converted to strings if necessary, i.e. only if `on`.
        Example of using `format`:
            explain = maybe_viewer(debug)
            # the next line will always convert x to string, even if debug is False:
            explain('Did a thing to: {}'.format(x))
            # the next line will hit the input string with .format(*[x]), only if debug is True:
            explain('Did a thing to: {}', format=[x])
        Note the format kwarg is only compatible when there is 1 arg entered, for simplicity.

    [EFF] Note: always more efficient to check the "do I print?" condition elsewhere,
        and only call a function if the answer is "yes".
        However, the code could be more readable by using maybe_viewer instead.
    '''
    if on:
        display_view = view   # this is the function view() from above (in the display.py namespace)
        def print_and_view(*args, view=None, format=[], **kw):
            if len(args)>0:
                if len(args)==1:
                    pstr = args[0] if len(format)==0 else args[0].format(*format)
                    print(pstr, **kw)
                elif len(format) > 0:
                    raise InputConflictError('kwarg "format" incompatible with entering multiple args!')
                else:
                    print(*args, **kw)
            if view is not None:
                display_view(view)
        return print_and_view
    else:
        def do_nothing(*args__None, **kw__None):
            pass
        return do_nothing

class MaybeViewer():
    '''when called, either self.print_and_view (if `on`), or self.do_nothing (if not `on`).
    Can use queue=True during self.print_and_view() to queue prints for later

    when evaluated as a boolean, return bool(self.on).
    '''
    view = staticmethod(view)  # << use self.view to view something, if view is not None during print_and_view.

    # # # INIT & PROPERTIES # # #
    def __init__(self, on=False):
        self.on = on
        self.queue = []  # list of (*args, **kw) tuples for queued calls to print_and_view.

    @property
    def on(self):
        '''whether to print_and_view when self is called. If False, do_nothing instead.'''
        try:
            return self._on
        except AttributeError:
            self._on = OnOffSwitch(False, 'Whether to print_and_view. If False, do_nothing instead.')
            return self._on
    @on.setter
    def on(self, value):
        '''sets new value for self.on.'''
        self.on.set(value)

    def __bool__(self):
        return bool(self.on)

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(on={repr(self.on)})'

    # # # CALL # # #
    def __call__(self, *args, view=None, format=[], queue=None, **kw):
        '''does self.print_and_view if self.on, else self.do_nothing.
        For help see help(self.print_and_view).
        '''
        if self.on:
            self.print_and_view(*args, view=view, format=format, queue=queue, **kw)
        else:
            self.do_nothing()

    def print_and_view(self, *args, view=None, format=[], queue=None, **kw):
        '''prints args, then does display.view(view).
        behavior affected by number of args:
            0 args --> print nothing.
            1 arg  --> print(args[0].format(*format), **kw)  # if format is [], skip formatting.
            >=2 args --> print(*args, **kw)   # Also, format not allowed in this case.
        format: list, default empty list.
            if converting objects to strings is non-trivial, you can pass them in to the `format` kwarg,
            so that they are only converted to strings if necessary, i.e. only if self.on.
            Example:
                explain = MaybeViewer(debug)
                # the next line will always convert x to string, even if debug is False:
                explain('Did a thing to: {}'.format(x))
                # the next line will hit the input string with .format(*[x]), only if debug is True:
                explain('Did a thing to: {}', format=[x])
            Note the format kwarg is only compatible when there is 1 arg entered, for simplicity.
        queue: None or bool, default None
            whether to remember inputs to print later, instead of printing now.
                True --> add to queue, then return without printing anything
                None --> self.unload_queue(), then print_and_view the current inputs.
                        i.e. print_and_view anything waiting in the queue, then handle current inputs.
                False --> just handle current inputs; don't consider the queue at all.
            Useful to print if any of multiple later conditions is met.
        '''
        # queue handling
        if queue:
            self.queue.append((args, dict(view=view, format=format, **kw)))
            return
        elif queue is None:
            self.unload_queue()
        # main functionality
        if len(args)>0:
            if len(args)==1:
                pstr = args[0] if len(format)==0 else args[0].format(*format)
                print(pstr, **kw)
            elif len(format) > 0:
                raise InputConflictError('kwarg "format" incompatible with entering multiple args!')
            else:
                print(*args, **kw)
        if view is not None:
            self.view(view)

    def unload_queue(self):
        '''prints things from the queue in self, then sets self.queue = [].'''
        for qd in self.queue:
            self.print_and_view(*qd[0], **qd[1], queue=False)
        self.queue = []

    def do_nothing(self, *args__None, **kw__None):
        '''accepts all args and kwargs, but does nothing.'''
        pass

maybe_viewer = MaybeViewer


''' --------------------- Misc. --------------------- '''

def print_clear(N=80):
    '''clears current printed line of up to N characters, and returns cursor to beginning of the line.
    debugging: make sure to use print(..., end=''), else your print statement will go to the next line.
    '''
    print('\r'+ ' '*N +'\r',end='')

def help_str(f):
    '''gets string from help(f)'''
    return pydoc.render_doc(f, '%s')