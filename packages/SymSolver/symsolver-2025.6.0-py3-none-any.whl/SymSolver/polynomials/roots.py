"""
File Purpose: methods related to roots of polynomials.

Recommended: use 'deval' mode for PolyFraction.roots_careful.
    The idea is that if the denominator is close to 0, the root is "bad";
    See poly_errors for details on how to determine what is "close to 0".
"""

from ..tools import ImportFailed
try:
    import numpy as np
except ImportError as err:
    np = ImportFailed('numpy', err=err)
try:
    import mpmath as mpm
except ImportError as err:
    mpm = ImportFailed('mpmath', err=err)

from .poly_to_array import PolyMPArray
from .polynomial import Polynomial
from .polyfraction import PolyFraction
from ..errors import (
    PolynomialPatternError, PolyFractionPatternError,
    PolynomialNotImplementedError,
    InputError, InputConflictError,
)
from ..tools import (
    array_select_max_imag, array_select_min_imag,
    array_select_max_real, array_select_min_real,
    Binding, format_docstring, alias,
)
from ..defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- roots tools --------------------- '''

_root_select_paramdocs = '''roots: array
        E.g. array of shape (70,50,3) for roots of 70 x 50 cubic polynomials.
    axis: int, default -1
        axis where the roots are listed.
    keepdims: bool, default False
        whether to keep dimensions of result.
        E.g. for (70,50,3) shape input, result will have shape (70,50,1) if keepdims, else (70,50).'''

@format_docstring(paramdocs=_root_select_paramdocs)
def roots_max_imag(roots, axis=-1, keepdims=False):
    '''selects root with maximum imaginary part.
    Note this is just an alias to tools.array_select_max_imag.

    {paramdocs}   
    '''
    return array_select_max_imag(roots, axis=-1, keepdims=keepdims)

@format_docstring(paramdocs=_root_select_paramdocs)
def roots_min_imag(roots, axis=-1, keepdims=False):
    '''selects root with minimum imaginary part.
    Note this is just an alias to tools.array_select_min_imag.

    {paramdocs}   
    '''
    return array_select_min_imag(roots, axis=-1, keepdims=keepdims)

@format_docstring(paramdocs=_root_select_paramdocs)
def roots_max_real(roots, axis=-1, keepdims=False):
    '''selects root with maximum real part.
    Note this is just an alias to tools.array_select_max_real.

    {paramdocs}   
    '''
    return array_select_max_real(roots, axis=-1, keepdims=keepdims)

@format_docstring(paramdocs=_root_select_paramdocs)
def roots_min_real(roots, axis=-1, keepdims=False):
    '''selects root with minimum real part.
    Note this is just an alias to tools.array_select_min_real.

    {paramdocs}   
    '''
    return array_select_min_real(roots, axis=-1, keepdims=keepdims)


''' --------------------- roots for a single Polynomial or PolyFraction --------------------- '''

with binding.to(Polynomial):
    @binding
    def numpy_roots(self, **kw__None):
        '''returns roots of self, by converting self to a single numpy polynomial and getting its roots.
        Requies all coefficients of self to be non-iterable. (E.g., not arrays. See also: self.to_mp_array().)
        '''
        np_poly = self._to_numpy_single(monicize=DEFAULTS.POLYROOTS_MONICIZE)
        return np_poly.roots()

    @binding
    @format_docstring(default_extraprec=DEFAULTS.POLYROOTS_EXTRAPREC)
    def mpmath_roots(self, *, extraprec=None, as_array=True, **kw__mpmath_polyroots):
        '''returns roots of self, by using mpmath.polyroots.
        Requies all coefficients of self to be non-iterable. (E.g., not arrays. See also: self.to_mp_array().)

        extraprec: None or int
            extra precision to use during root-find algorithm; passed directly to mpmath.polyroots.
            None --> use DEFAULTS.POLYROOTS_EXTRAPREC (default: {default_extraprec})
        as_array: bool, default True
            whether to convert result of mpmath.polyroots to array (of complex numbers), before returning.
            True --> convert result to array of complex numbers.
            False --> return result of mpmath.polyroots, unchanged. CAUTION: issues if applying numpy funcs.
                    (example issue: np.imag(result) will be an array of 0's.)

        extra kwargs are passed directly to mpmath.polyroots.
        '''
        if extraprec is None: extraprec = DEFAULTS.POLYROOTS_EXTRAPREC
        coeff = self.coef_list(reverse=True, iterable_ok=False)
        result = mpm.polyroots(coeff, extraprec=extraprec, **kw__mpmath_polyroots)
        return np.array(result, dtype=complex) if as_array else result

    Polynomial.np_roots = alias('numpy_roots')
    Polynomial.mpm_roots = alias('mpmath_roots')

    @binding
    @format_docstring(default_mode=DEFAULTS.POLYROOTS_MODE, default_easycheck=DEFAULTS.POLYROOTS_EASYCHECK)
    def roots(self, roots_mode=None, *, _easy_check=None, **kw):
        '''return roots of self.
        Requies all coefficients of self to be non-iterable. (E.g., not arrays. See also: self.to_mp_array().)

        roots_mode: None or str
            how to calculate the roots.
            None --> use DEFAULTS.POLYROOTS_MODE  (default: {default_mode})
            'numpy' or 'np' --> use self.numpy_roots(**kw)
            'mpmath' or 'mpm' --> use self.mpmath_roots(**kw)
        _easy_check: None or bool, default None
            whether to check self.easy_roots() first.
            [EFF] Improves efficiency if self has easy roots (e.g. quadratic or linear).
            None --> use DEFAULTS.POLYROOTS_EASYCHECK   (default: {default_easycheck})
        '''
        # easycheck?
        if _easy_check is None: _easy_check = DEFAULTS.POLYROOTS_EASYCHECK
        if _easy_check:
            try:
                return self.easy_roots(**kw)
            except (PolynomialNotImplementedError, PolynomialPatternError):
                pass  # no easy roots found; do more generic root finding.
        # setup
        if roots_mode is None:
            roots_mode = DEFAULTS.POLYROOTS_MODE
        # find roots
        if roots_mode in ('numpy', 'np'):
            result = self.numpy_roots(**kw)
        elif roots_mode in ('mpmath', 'mpm'):
            result = self.mpmath_roots(**kw)
        else:
            raise InputError(f"invalid roots_mode. Expected 'numpy' or 'mpmath' but got {repr(roots_mode)}")
        self._latest_roots_method = roots_mode
        return result

    @binding
    def easy_roots(self, **kw__None):
        '''gets roots using a simple formula. raise error if this is not possible.
        (error type will be PolynomialPatternError OR PolynomialNotImplementedError)
        Simple formulae attempted here include:
            a x + b --> -b / a
            a x^2 + b x + c --> (-b +- sqrt(b^2 - 4 a c)) / (2 a)

        returns: array of roots; result[i] is i'th root
            if self implies an array of polynomials (i.e. self has array coefs),
            then result[..., i] is i'th root, instead.
            This is true even if there is only 1 root.
            E.g. input with coefs of shape (4,5) -->
                result of shape (4,5,2) for quadratic, or (4,5,1) for linear.
        '''
        if len(self) > 3:  # more than 3 terms: degree 3+, or some terms with negative power.
            raise PolynomialNotImplementedError('No easy roots for polynomial with len > 3')
        coefs = self.coef_list(reverse=True)  # highest-power to lowest-power. Crashes if any power is negative.
        L = len(coefs)
        if len(coefs) > 3:  # degree 3+
            raise PolynomialNotImplementedError('No easy roots for polynomial with degree > 2')
        if len(coefs) == 3:  # degree 2: x^2, x^1, x^0. (3 terms)
            a, b, c = coefs
            t2 = np.emath.sqrt(b**2 - 4*a*c) / (2*a)  # emath.sqrt(real input < 0) --> complex; sqrt(...) --> nan.
            t1 = -b / (2*a)
            root1 = t1 - t2
            root2 = t1 + t2
            result = np.concatenate([np.expand_dims(root1, axis=-1), np.expand_dims(root2, axis=-1)], axis=-1)
        elif len(coefs) == 2:  # degree 1: x^1, x^0.  (2 terms)
            a, b = coefs
            result = np.expand_dims(-b / a, axis=-1)
        else:
            raise PolynomialPatternError('No easy roots for polynomial with degree == 0')
        self._latest_roots_method = 'easy'
        return result

    @binding
    @format_docstring(default_mode=DEFAULTS.POLYROOTS_MODE, default_easycheck=DEFAULTS.POLYROOTS_EASYCHECK)
    def array_roots(self, roots_mode=None, *, expand=True, _easy_check=None, **kw):
        '''return array of roots from self (with array coefficients).
        returns self.easy_roots(**kw) if possible,
        otherwise self.to_mp_array().apply('roots', **kw).

        Also sets self._latest_array_roots_method to 'easy', or roots_mode.

        roots_mode: None or str
            how to calculate the roots, if self.roots_easy() fails.
            None --> use DEFAULTS.POLYROOTS_MODE  (default: {default_mode})
            'numpy' or 'np' --> use self.numpy_roots(**kw)
            'mpmath' or 'mpm' --> use self.mpmath_roots(**kw)
        expand: bool, default True
            whether to expand array elements from apply('roots').
            True --> result will have shape (*self.shape, N roots per polynomial)
            False --> result will have same shape as self, and each element will be a list of roots.
        _easy_check: None or bool, default None
            whether to check self.easy_roots() first.
            [EFF] Improves efficiency if self has easy roots (e.g. quadratic or linear).
            None --> use DEFAULTS.POLYROOTS_EASYCHECK   (default: {default_easycheck})

        Might consume lots of memory / time.
        [EFF] For direct usage, recommend to call these separately,
        e.g. separately store self.to_mp_array(), in case you want to re-use it.
        '''
        # [TODO](maybe) implement caching for result of self.to_mp_array(), instead?
        roots = None
        if _easy_check is None: _easy_check = DEFAULTS.POLYROOTS_EASYCHECK
        if _easy_check:
            try:
                roots = self.easy_roots(**kw)
            except PolynomialPatternError:
                pass  # << easy check failed; handle below.
        if roots is None:
            parr = self.to_mp_array()
            roots = parr.apply('roots', roots_mode=roots_mode, expand=expand, **kw)
        self._latest_array_roots_method = self._latest_roots_method
        return roots


with binding.to(PolyFraction):
    @binding
    def roots(self, careful=False, **kw__roots):
        '''returns roots of numerator. Assumes numerator has numerical coefficients, each of which is non-iterable.

        careful: bool or str, default False
            whether to check that roots are okay.
            False --> return self.numer.roots(), without checking if they are okay.
            True --> return self.roots_careful(mode=DEFAULTS.POLYFRACTION_CAREFUL_ROOTS_MODE)
            str --> return self.roots_careful(mode=careful)

            For example, in (x**2 + 4x + 3) / (x+1 + 1e-50),
                x=-1 is a root of the numerator but not the denominator.
                However, what if that 1e-50 comes from floating point errors? It's hard to know for sure.
                To be safe, we may want to reject the x=-1 root.
                Due to the ambiguity, there are different options for how to be careful about the roots.
            [EFF] being careful is more computationally expensive but helps prevent misleading results.
        
        See help(self.roots_careful) for details on options for determining whether roots are "okay" or not.
        '''
        if careful:
            careful, mode = self._careful_and_mode(careful, **kw__roots)
            kw__roots['mode'] = mode
            return self.roots_careful(**kw__roots)
        else:
            return self.numer.roots(**kw__roots)

    @binding
    def _careful_and_mode(self, careful=False, mode=None, **kw__None):
        '''return careful, mode, after checking for input conflicts.
        if careful is a str, mode must equal careful, if provided.
        '''
        if isinstance(careful, str):
            if (mode is not None) and (mode != careful):
                raise InputConflictError(f'careful={careful}, mode={mode}')
            mode = careful
            careful = True
        return careful, mode


''' --------------------- roots sorted --------------------- '''

with binding.to(Polynomial, PolyFraction):
    @binding
    def roots_sorted(self, key=lambda roots: roots, reverse=False, **kw__roots):
        '''return roots of self, sorted via np.argsort(key(roots)).
        if reverse, return result[::-1] instead.
        '''
        roots = self.roots(**kw__roots)
        result = roots[np.argsort(key(roots))]
        if reverse:
            return result[::-1]
        else:
            return result

    @binding
    def roots_sorted_by_imag(self, descending=True, **kw__roots):
        '''returns roots of self, sorted by imaginary part. (default: largest first.)

        descending: bool, default True
            whether to go from largest imaginary part to smallest imaginary part.
            (e.g. if True, the root with largest imaginary part will be first.)
        '''
        return self.roots_sorted(key=np.imag, reverse=descending, **kw__roots)


''' --------------------- roots_are_bad test. (for PolyFraction) --------------------- '''

_tol_mode_docs = '''tol: None, value, or tuple.
            tolerance for "small" / when a root is "bad". Meaning depends on mode...
        mode: None, 'deval', 'evaluate', or 'compare'
            None --> use DEFAULTS.POLYFRACTION_CAREFUL_ROOTS_MODE
            'deval' --> root "bad" if self.denom(root) is close to 0.
                i.e., "bad" if |self.denom(root)| < self.denom.error_scale(root) * 1/tol.
                if tol is None, use getattr(self, '_roots_dtol', DEFAULTS.POLYFRACTION_ROOTS_DTOL)
            'evaluate' --> root "bad" if pf(root) is not close to 0.
                i.e., "bad" if |self(root)| > tol.
                if tol is None, use getattr(self, '_roots_tol', DEFAULTS.POLYFRACTION_ROOTS_TOL)
            'matching' --> root "bad" if root matches (is close to) any denom.roots().
                i.e., reject if any(np.isclose(dr, root, rtol=tol[0], atol=tol[1]) for dr in self.denom.roots()).
                if tol is None, use getattr(self, '_roots_ratol', DEFAULTS.POLYFRACTION_ROOTS_RATOL)'''

with binding.to(PolyFraction):
    @binding
    @format_docstring(_tol_mode_docs=_tol_mode_docs)
    def roots_are_bad(self, roots, mode=None, *, tol=None, denom_roots=None):
        '''check which roots are "bad".
        returns array of True/False values, of same length as roots, with
            result[i] True  <--> roots[i] is BAD
            result[i] False <--> roots[i] is okay.

        roots: any values
            determine if these are "bad". meaning of "bad" depends on tol & mode.
        {_tol_mode_docs}
        denom_roots: None, or array of values
            [EFF] if provided, and using 'compare' mode, use these values instead of self.denom.roots().
        '''
        tol, mode = self._tol_and_mode(tol, mode)
        roots = np.asanyarray(roots)
        if mode == 'deval':
            denom_at_roots = self.denom(roots)
            errscale_at_roots = self.denom.error_scale(roots)
            return (np.abs(denom_at_roots) < errscale_at_roots * (1/tol))
        elif mode == 'evaluate':
            vals = self(roots)
            return (np.isnan(vals) | (np.abs(vals) > tol))
        elif mode == 'compare':
            if denom_roots is None:
                denom_roots = self.denom.roots()
            results = [np.any(np.isclose(denom_roots, root, rtol=tol[0], atol=tol[1])) for root in roots]
            return np.array(results)
        else:
            raise NotImplementedError(f'invalid mode: {mode!r}')

    @binding
    @format_docstring(_tol_mode_docs=_tol_mode_docs)
    def root_is_bad(self, root, mode=None, *, tol=None, denom_roots=None):
        '''check whether this root is "bad".
        returns:
            False <--> root is "okay"
            True  <--> root is "BAD"

        root: any value
            determine if this root is "bad". meaning of "bad" depends on tol & mode.
        {_tol_mode_docs}
        denom_roots: None or array of values
            [EFF] if provided, and using 'compare' mode, use these values instead of self.denom.roots().

        equivalent to self.roots_are_bad([root], ...)[0]
        '''
        result = self.roots_are_bad([root], mode=mode, tol=tol, denom_roots=denom_roots)  # result as a list
        return result[0]

    @binding
    @format_docstring(_tol_mode_docs=_tol_mode_docs)
    def _tol_and_mode(self, tol=None, mode=None):
        '''returns (tolerance, mode) to use for determining whether roots are bad.

        {_tol_mode_docs}
        '''
        if mode is None:
            mode = DEFAULTS.POLYFRACTION_CAREFUL_ROOTS_MODE
        VALID_MODES = {'deval', 'evaluate', 'compare'}
        assert mode in VALID_MODES, f'invalid mode: {mode!r}'
        if tol is None:
            if mode == 'deval':
                tol = getattr(self, '_roots_dtol', DEFAULTS.POLYFRACTION_ROOTS_DTOL)
            elif mode == 'evaluate':
                tol = getattr(self, '_roots_tol', DEFAULTS.POLYFRACTION_ROOTS_TOL)
            else: # mode == 'compare'
                tol = getattr(self, '_roots_ratol', DEFAULTS.POLYFRACTION_ROOTS_RATOL)
        return (tol, mode)


''' --------------------- Methods for selecting good / bad roots --------------------- '''
# (utilizing the roots_are_bad test from the previous section)

with binding.to(PolyFraction):
    @binding
    @format_docstring(_tol_mode_docs=_tol_mode_docs)
    def roots_careful(self, mode=None, *, tol=None, denom_roots=None, **kw__roots):
        '''returns roots of self, after removing any "bad" roots. "bad" determined by mode & tol.

        This function mitigates the issue that self.roots() only checks roots of numerator,
        so if denominator shares any of those roots then self.roots() may be misleading.
        For example, x=-1 should not be a root of (x**2 + 4x + 3) / (x+1), but it is a root of the numerator.

        {_tol_mode_docs}
        denom_roots: None, or array of values
            [EFF] if provided, and using 'compare' mode, use these values instead of self.denom.roots().

        [EFF] This is more computationally expensive than self.roots(careful=False)
        '''
        all_roots = self.roots(careful=False, **kw__roots)
        return self.select_good_roots(all_roots, tol=tol, mode=mode)

    @binding
    @format_docstring(_tol_mode_docs=_tol_mode_docs)
    def first_good_root(self, sortby=lambda roots: roots, *, reverse=False,
                        tol=None, mode=None,
                        simultest=None, denom_roots=None, **kw__roots):
        '''returns first root of self which is a non-"bad" root. "bad" determined by tol & mode.
        
        sortby: function(roots). Default: roots --> roots.
            sort roots according to this order, via np.argsort(sortby(roots)).
            Example: to sort by imaginary part, use
                lambda roots: np.imag(roots)
        reverse: bool, default False
            whether to reverse the result from sorting.
            Example: to sort by imaginary part, in reverse order (i.e. with largest first), use
                sortby = lambda roots: np.imag(roots);  reverse = True
        {_tol_mode_docs}

        simultest: None or bool, default None
            [EFF] whether to test all roots at once (self.roots_are_bad).
            When False, test roots one at a time, returning the first non-bad root found.
            None --> use True if mode == 'deval' or 'evaluate', else False.
            This is an option for efficiency; if commonly rejecting the first few roots,
                if will probably be faster to test all at once (if using 'deval' or 'evaluate' mode),
                due to numpy optimizations / vectorization.
                If commonly accepting the first or second root, this option will probably be slower.
        denom_roots: None or array of values
            [EFF] if provided, and using 'compare' mode, use these values instead of self.denom.roots().

        returns root.
        If NO roots are good, instead returns np.nan (or np.nan + np.nan * 1j if any roots are complex).
        '''
        # get sorted roots
        roots = self.roots(**kw__roots)
        roots_argsort = np.argsort(sortby(roots))
        if reverse:
            roots_argsort = roots_argsort[::-1]
        tol, mode = self._tol_and_mode(tol, mode)
        if (mode == 'compare') and (denom_roots is None):
            denom_roots = self.denom.roots()  # [EFF] calculate only once, for efficiency.
        if simultest is None: simultest = (mode in ('deval', 'evaluate'))
        # test roots:
        if simultest:
            is_bad = self.roots_are_bad(roots, mode=mode, tol=tol, denom_roots=denom_roots)
            for i in roots_argsort:
                if not is_bad[i]:
                    return roots[i]
        else:
            for i in roots_argsort:
                root = roots[i]
                is_bad = self.root_is_bad(root, mode=mode, tol=tol, denom_roots=denom_roots)
                if not is_bad:
                    return root
        # didn't find any good root
        any_complex = any(isinstance(root, complex) for root in roots)
        return (np.nan + 1j * np.nan) if any_complex else np.nan

    @binding
    def select_bad_roots(self, roots, mode=None, *, tol=None, denom_roots=None):
        '''returns array of all values from roots which are BAD roots.
        "bad root" if |self(root)| > tol, i.e. if self(root) is NOT "close to 0".

        see help(self.roots_are_bad) for details on inputs.
        '''
        roots = np.asanyarray(roots)
        return roots[self.roots_are_bad(roots, tol=tol, mode=mode, denom_roots=denom_roots)]

    @binding
    def select_good_roots(self, roots, mode=None, *, tol=None, denom_roots=None):
        '''returns array of all values from roots which are good roots.
        "good root" if |self(root)| <= tol, i.e. if self(root) is "close to 0".

        see help(self.roots_are_bad) for details on inputs.
        '''
        roots = np.asanyarray(roots)
        return roots[~self.roots_are_bad(roots, tol=tol, mode=mode, denom_roots=denom_roots)]

    @binding
    def count_roots(self, **kw__roots):
        '''returns len(self.roots(**kw__roots))
        Convenience method, useful with MPArray.apply for debugging / inspecting data.
        '''
        return len(self.roots(**kw__roots))

    @binding
    def count_roots_good_and_bad(self, **kw__roots):
        '''returns (number of good roots, number of bad roots).'''
        roots = self.roots(**kw__roots)
        roots_careful = self.select_good_roots(roots)
        Ngood = len(roots_careful)
        return (Ngood, len(roots) - Ngood)


''' --------------------- roots pick max or min --------------------- '''

with binding.to(Polynomial):
    Polynomial.growth_root = alias('root_max_imag')

    @binding
    def root_max_imag(self, **kw__roots):
        '''returns the root from self with the largest imaginary part.'''
        roots = self.roots(**kw__roots)
        return roots[np.argmax(np.imag(roots))]

    @binding
    def root_min_imag(self, **kw__roots):
        '''returns the root from self with the smallest imaginary part.'''
        roots = self.roots(**kw__roots)
        return roots[np.argmin(np.imag(roots))]

    @binding
    def root_max_real(self, **kw__roots):
        '''returns the root from self with the largest real part.'''
        roots = self.roots(**kw__roots)
        return roots[np.argmax(np.real(roots))]

    @binding
    def root_min_real(self, **kw__roots):
        '''returns the root from self with the smallest real part.'''
        roots = self.roots(**kw__roots)
        return roots[np.argmin(np.real(roots))]


with binding.to(PolyFraction):
    _careful_tol_paramdocs = \
        f'''careful: bool or str, default True
            True --> check to ensure that the result is a non-"bad" root of self.
                    if it is a "bad" root, try the next root instead (repeating as necessary).
            False --> don't check whether roots are okay; just use self.roots().
            str --> use mode=careful. Be sure to avoid providing a conflicting value of mode in kwargs.
        {_tol_mode_docs}'''

    @binding
    @format_docstring(paramdocs=_careful_tol_paramdocs)
    def _root_pick_from_key(self, sortby=lambda roots: roots, *, reverse=False,
                            careful=True, mode=None, tol=None, **kw__roots):
        '''returns first root from self...

        sortby: function(roots) --> list
            sort roots by this function, to determine order of roots, so that "first" can be chosen.
            default: roots --> roots, unchanged.
        reverse: bool, default False
            whether to reverse the sorted list after sortby(roots).
        {paramdocs}
        '''
        if careful:
            careful, mode = self._careful_and_mode(careful, mode)
            return self.first_good_root(sortby=sortby, reverse=reverse, tol=tol, mode=mode, **kw__roots)
        else:
            return self.roots_sorted(key=sortby, reverse=reverse, **kw__roots)[0]

    PolyFraction.growth_root = alias('root_max_imag')

    @binding
    @format_docstring(paramdocs=_careful_tol_paramdocs)   
    def root_max_imag(self, careful=True, **kw):
        '''returns the root from self with the largest imaginary part.

        {paramdocs}
        '''
        return self._root_pick_from_key(sortby=np.imag, reverse=True, careful=careful, **kw)

    @binding
    @format_docstring(paramdocs=_careful_tol_paramdocs)   
    def root_min_imag(self, careful=True, **kw):
        '''returns the root from self with the largest imaginary part.

        {paramdocs}
        '''
        return self._root_pick_from_key(sortby=np.imag, reverse=False, careful=careful, **kw)

    @binding
    @format_docstring(paramdocs=_careful_tol_paramdocs)   
    def root_max_real(self, careful=True, **kw):
        '''returns the root from self with the largest imaginary part.

        {paramdocs}
        '''
        return self._root_pick_from_key(sortby=np.real, reverse=True, careful=careful, **kw)

    @binding
    @format_docstring(paramdocs=_careful_tol_paramdocs)   
    def root_min_real(self, careful=True, **kw):
        '''returns the root from self with the largest imaginary part.

        {paramdocs}
        '''
        return self._root_pick_from_key(sortby=np.real, reverse=False, careful=careful, **kw)


''' --------------------- roots convenience for PolyMPArray --------------------- '''

with binding.to(PolyMPArray):
    @binding
    def roots(self, *args, expand=True, **kw):
        '''returns self.apply('roots', *args, expand=expand, **kw).astype(complex)'''
        return self.apply('roots', *args, expand=expand, **kw).astype(complex)

    PolyMPArray.growth_root = alias('root_max_imag')

    @binding
    def root_max_imag(self, *args, **kw):
        '''returns self.apply('root_max_imag', *args, **kw).astype(complex)'''
        return self.apply('root_max_imag', *args, **kw).astype(complex)

    @binding
    def root_min_imag(self, *args, **kw):
        '''returns self.apply('root_min_imag', *args, **kw).astype(complex)'''
        return self.apply('root_min_imag', *args, **kw).astype(complex)

    @binding
    def root_max_real(self, *args, **kw):
        '''returns self.apply('root_max_real', *args, **kw).astype(complex)'''
        return self.apply('root_max_real', *args, **kw).astype(complex)

    @binding
    def root_min_real(self, *args, **kw):
        '''returns self.apply('root_min_real', *args, **kw).astype(complex)'''
        return self.apply('root_min_real', *args, **kw).astype(complex)
