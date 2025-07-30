"""
File Purpose: convert Polynomial (or PolyFraction) into numpy array or MPArray

to_array() --> to numpy array of Polynomial (or PolyFraction) objects.
to_mp_array() --> to MPArray storing self.to_array()
to_numpy_array() --> to array of numpy.polynomial.Polynomial objects  (only for SymSolver.Polynomial)

MPArray provides the 'apply' method for applying a function to each object in the array.

[TODO] encapsulate the broadcasting code here, instead of copy-pasting most of it.
"""

from ..tools import ImportFailed
try:
    import numpy as np
except ImportError as err:
    np = ImportFailed('numpy', err=err)

from .polynomial import Polynomial
from .polyfraction import PolyFraction
from ..errors import (
    PolynomialPatternError, PolyFractionPatternError,
    ImportFailedError,
)
from ..tools import (
    ProgressUpdater,
    format_docstring,
    UNSET,
    is_integer,
    Binding,
    itarrayte, ContainerOfArray,
    TaskArray, TaskContainerCallKwargsAttrHaver, _paramdocs_tasks,
)
from ..defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- to_array() --------------------- '''

with binding.to(Polynomial):
    @binding
    def to_array(self, *, fast=None, fast_threshold=10000, print_freq=None):
        '''converts self into an array of Polynomials.
        if all coefs are scalars, the output will have shape ().
            Note: to get the scalar from an array with shape (), use [()]. E.g. np.array(7)[()] --> 7
        otherwise, the output will have the shape implied by numpy broadcasting rules.
            (The coefficients must be broadcastable with each other)

        fast: bool or None, default True
            None --> fast if result.size > fast_threshold, else not fast.
            fast --> instead of using self._new, use type(self)(..., var=var)
                        This might discard other nice properties tracked by usual SymSolver ._new,
                        but it can be noticeably faster.
                    Additionally, only print progress at most every 1000 steps,
                        to reduce number of calls to updater.print.
        '''
        updater = ProgressUpdater(print_freq, wait=True)
        # bookkeeping related to broadcasting
        updater.print('doing bookkeeping / broadcasting for to_array()')
        keys, coefs  = zip(*self.items())
        broad_arrays = np.broadcast_arrays(*coefs, subok=True)
        coefs_broad  = np.asanyarray(broad_arrays[:])
        broad_shape  = np.broadcast_shapes(*(c.shape for c in coefs_broad))
        if len(broad_arrays) == 0:
            raise PolynomialPatternError('cannot convert Polynomial with no coefficients to array.')
        # get result
        result = np.empty(broad_shape, dtype=object)
        size = result.size
        if fast is None:
            fast = (size > fast_threshold)
        if fast:
            var = self.var
            newself = type(self)
            for ii, (_, midx) in enumerate(itarrayte(broad_arrays[0])):
                if ii % 1000 == 0: updater.print(f'Converting to SymSolver.Polynomial; {ii:5d} of {size:5d}')
                # put result[midx] equal to the (midx)'th polynomial
                slicer = tuple((slice(None), *midx))
                this_poly = newself( { key: coef for key, coef in zip(keys, coefs_broad[slicer]) }, var=var)
                result[midx] = this_poly
        else:
            for ii, (_, midx) in enumerate(itarrayte(broad_arrays[0])):
                if ii % 1000 == 0: updater.print(f'Converting to SymSolver.Polynomial; {ii:5d} of {size:5d}')
                # put result[midx] equal to the (midx)'th polynomial
                slicer = tuple((slice(None), *midx))
                this_poly = self._new( { key: coef for key, coef in zip(keys, coefs_broad[slicer]) })
                result[midx] = this_poly
        updater.finalize(process_name='Polynomial.to_array()')
        return result

with binding.to(PolyFraction):
    @binding
    def to_array(self, *, fast=None, fast_threshold=10000, print_freq=None):
        '''converts self into an array of PolyFractions.
        if all coefs are scalars, the output will have shape ().
            Note: to get the scalar from an array with shape (), use [()]. E.g. np.array(7)[()] --> 7
        otherwise, the output will have the shape implied by numpy broadcasting rules.
            (The coefficients must be broadcastable with each other)

        NOTE: not really compatible with masked arrays.
        Instead of using masked arrays, it is recommended to index the input arrays by the mask.

        fast: bool or None, default True
            None --> fast if result.size > fast_threshold, else not fast.
            fast --> instead of using self._new, numer._new, and denom._new,
                    use type(self)(..., var=var), type(numer)(..., var=var), type(denom)(..., var=var).
                        This might discard other nice properties tracked by usual SymSolver ._new,
                        but it can be noticeably faster.
                    Additionally, only print progress at most every 1000 steps,
                        to reduce number of calls to updater.print.
        '''
        updater = ProgressUpdater(print_freq, wait=True)
        # bookkeeping related to broadcasting
        updater.print('doing bookkeeping / broadcasting for to_array()')
        nkeys, ncoefs = zip(*self.numer.items())
        dkeys, dcoefs = zip(*self.denom.items())
        len_n         = len(ncoefs)
        broad_arrays = np.broadcast_arrays(*ncoefs, *dcoefs, subok=True)
        ncoefs_broad = np.asarray(broad_arrays[:len_n])
        dcoefs_broad = np.asarray(broad_arrays[len_n:])
        broad_shape  = np.broadcast_shapes(*(c.shape for c in ncoefs_broad), *(d.shape for d in dcoefs_broad))
        if len(broad_arrays) == 0:
            raise PolyFractionPatternError('cannot convert PolyFraction to array when len(numer)==len(denom)==0')
        # get result
        result = np.empty(broad_shape, dtype=object)
        size = result.size
        if fast is None:
            fast = (size > fast_threshold)
        if fast:
            var = self.var
            newnumer = type(self.numer)
            newdenom = type(self.denom)
            newself = type(self)
            for ii, (_, midx) in enumerate(itarrayte(broad_arrays[0])):
                if ii % 1000 == 0: updater.print(f'Converting to PolyFraction; {ii:5d} of {size:5d}')
                # put result[midx] equal to the (midx)'th polynomial
                slicer = tuple((slice(None), *midx))
                numer = newnumer({key: coef for key, coef in zip(nkeys, ncoefs_broad[slicer])}, var=var)
                denom = newdenom({key: coef for key, coef in zip(dkeys, dcoefs_broad[slicer])}, var=var)
                result[midx] = newself(numer, denom, var=var)
        else:
            for ii, (_, midx) in enumerate(itarrayte(broad_arrays[0])):
                updater.print(f'Converting to PolyFraction; {ii:5d} of {size:5d}')
                # put result[midx] equal to the (midx)'th polynomial
                slicer = tuple((slice(None), *midx))
                numer = self.numer._new({key: coef for key, coef in zip(nkeys, ncoefs_broad[slicer])})
                denom = self.denom._new({key: coef for key, coef in zip(dkeys, dcoefs_broad[slicer])})
                result[midx] = self._new(numer, denom)
        updater.finalize(process_name='PolyFraction.to_array()')
        return result


''' --------------------- to numpy --------------------- '''

with binding.to(Polynomial):
    @binding
    def to_numpy_array(self, print_freq=None, **kw__np_polynomial):
        '''converts self into an array of numpy polynomials.
        if all coefs are scalars, the output will have shape ().
            Note: to get the scalar from an array with shape (), use [()]. E.g. np.array(7)[()] --> 7
        otherwise, the output will have the shape implied by numpy broadcasting rules.
            (The coefficients must be broadcastable with each other)
        '''
        updater = ProgressUpdater(print_freq, wait=True)
        # bookkeeping related to broadcasting
        updater.print('doing bookkeeping / broadcasting for to_array()')
        coefs = self.coef_list(reverse=False)
        broad_arrays = np.broadcast_arrays(*coefs, subok=True)
        coefs_broad  = np.asanyarray(broad_arrays[:])
        broad_shape  = np.broadcast_shapes(*(c.shape for c in coefs_broad))
        if len(broad_arrays) == 0:
            raise PolynomialPatternError('cannot convert Polynomial with no coefficients to numpy.')
        # get result
        result = np.empty(broad_shape, dtype=object)
        size = result.size
        for ii, (_, midx) in enumerate(itarrayte(broad_arrays[0])):
            updater.print(f'Converting to numpy.polynomial.Polynomial ({ii:5d} of {size:5d})', print_time=True)
            # put result[midx] equal to the (midx)'th polynomial
            slicer = tuple((slice(None), *midx))
            this_poly = np.polynomial.Polynomial(coefs_broad[slicer], **kw__np_polynomial)
            result[midx] = this_poly
        updater.finalize(process_name='Polynomial.to_numpy()')
        return result

    @binding
    def _to_numpy_single(self, *, monicize=False, **kw__np_polynomial):
        '''converts self into a single numpy polynomial.
        requires that coefficients in self are 0-d (e.g. not lists, not (N>=1)-dimensional arrays).
        monicize: bool, default False
            if True, divide by largest-degree coefficient before returning result.
            Recommended if using result for root-finding; see DEFAULTS.POLYROOTS_MONICIZE
        '''
        coefs = np.asanyarray(self.coef_list(reverse=False, iterable_ok=False))
        if monicize:
            coefs = coefs / coefs[-1]
        result = np.polynomial.Polynomial(coefs, **kw__np_polynomial)
        return result


''' --------------------- to_mp_array() --------------------- '''

class PolyMPArray(ContainerOfArray, TaskContainerCallKwargsAttrHaver):
    '''ContainerOfArray with some defaults appropriate to root finding.
    self.apply(f) applies f to each element of array. see help(self.apply) for details.

    defaults appropriate to root finding:
        RESULT_MISSING = nan + 1j * nan,
        ERRORS_OK = (numpy.linalg.LinAlgError,)
    '''
    try:
        RESULT_MISSING = np.nan + 1j * np.nan
        ERRORS_OK = (np.linalg.LinAlgError,)
    except ImportFailedError:
        # numpy previously failed to import... set RESULT_MISSING and ERRORS_OK = np,
        # to help indicate to user that this is the reason PolyMPArray methods will fail.
        # Only crash when attempting to use it, but not immediately when loading SymSolver.
        RESULT_MISSING = np
        ERRORS_OK = np

    task_array_cls = TaskArray

    @format_docstring(**_paramdocs_tasks)
    def task_array(self, f, *args_f, errors_ok=UNSET, **kw_f):
        '''return a TaskArray for applying f to each polynomial in self.

        f: callable or string
            apply this to each element p, in self.
            callable --> tasks will do f(p, *args_f, **kw_f).
            else --> tasks will do p.f(*args_f, **kw_f).
        errors_ok: UNSET or {errors_ok}
            UNSET --> use self.ERRORS_OK (default (numpy.linalg.LinAlgError,))
            if errors_ok, tasks which crash will return np.nan + 1j * np.nan.
        '''
        task_inputs = self.new_empty()  # empty array with dtype=object, shape=self.shape.
        if callable(f):
            for idx, p in self.enumerate():
                task_inputs[idx] = (f, (p, *args_f), kw_f)
        else:  # f is a string, hopefully.
            for idx, p in self.enumerate():
                task_inputs[idx] = (getattr(p, f), args_f, kw_f)
        process_name = f'{type(self).__name__} applying to each poly: {f!r}'
        kw_mp = dict(printable_process_name=process_name,
                     errors_ok=self.ERRORS_OK,
                     result_missing=self.RESULT_MISSING)
        return self.task_array_cls(task_inputs, shape=self.shape, **kw_mp)

    @format_docstring(**_paramdocs_tasks, sub_ntab=1)
    def apply(self, f, *args_f, ncpu=UNSET, timeout=UNSET, ncoarse=UNSET,
              print_freq=UNSET, errors_ok=UNSET, result_missing=UNSET, **kw_f):
        '''return result of applying f to each polynomial in self.

        f: callable or string
            apply this to each element p, in self.
            callable --> tasks will do f(p, *args_f, **kw_f).
            else --> tasks will do p.f(*args_f, **kw_f).
        ncpu: UNSET or {ncpu}
            UNSET --> use self.ncpu (default None)
        timeout: UNSET or {timeout}
            UNSET --> use self.timeout (default None)
        ncoarse: UNSET or {ncoarse}
            UNSET --> use self.ncoarse (default 1)
        print_freq: UNSET or {print_freq}
            UNSET --> use self.print_freq (default None, i.e. use DEFAULTS.PROGRESS_UPDATES_PRINT_FREQ.)
        errors_ok: UNSET or {errors_ok}
            UNSET --> use self.ERRORS_OK (default (numpy.linalg.LinAlgError,))
        result_missing: UNSET or {result_missing}
            UNSET --> use self.RESULT_MISSING (default np.nan + 1j * np.nan)
        '''
        tasks = self.task_array(f, *args_f, **kw_f)
        if ncpu is UNSET: ncpu = self.ncpu
        if timeout is UNSET: timeout = self.timeout
        if ncoarse is UNSET: ncoarse = self.ncoarse
        if print_freq is UNSET: print_freq = self.print_freq
        if errors_ok is UNSET: errors_ok = self.ERRORS_OK
        if result_missing is UNSET: result_missing = self.RESULT_MISSING
        kw_mp = dict(ncpu=ncpu, timeout=timeout, ncoarse=ncoarse, print_freq=print_freq,
                     errors_ok=errors_ok, result_missing=result_missing)
        result = tasks(**kw_mp)
        return result


with binding.to(Polynomial, PolyFraction):
    @binding
    def to_mp_array(self, print_freq=None, **kw__to_array):
        '''return PolyMPArray(self.to_array()). kwargs go to to_array.'''
        self_as_array = self.to_array(print_freq=print_freq, **kw__to_array)
        return PolyMPArray(self_as_array)
