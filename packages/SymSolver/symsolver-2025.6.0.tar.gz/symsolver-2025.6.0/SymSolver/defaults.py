"""
File purpose: DEFAULTS contains defaults and documentation.

See DEFAULTS.help() for details on which defaults are available.
Set attributes of DEFAULTS to change the defaults globally in SymSolver.
  E.g. DEFAULTS.RENDER_MATH.enable() enables rendering math.
"""

from inspect import getdoc
from textwrap import indent

''' ----------------------------- setup ----------------------------- '''

class EmptyClass():   # just an empty class.
    pass

class OnOffSwitch():
    '''flippable switch.
    (Using OnOffSwitch for default values --> the value can be changed globally by anyone who has access.)
    '''
    def __init__(self, state, doc=None):
        self.state = state
        self.doc = doc
    def __bool__(self): return bool(self.state)
    def enable(self):
        self.state = True
    def disable(self):
        self.state = False
    def set(self, value):
        self.state = bool(value)
    on  = property(lambda self: self.enable, doc='''alias for enable''')
    off = property(lambda self: self.disable, doc='''alias for disable''')
    def flip(self):
        self.state = not self.state
        return self.state
    def __repr__(self):
        prettyspace = ' ' if self.state else ''  # "True" has 1 fewer letters than "False".
        docstr = '' if self.doc is None else f'.{prettyspace} {self.doc}'
        return f'{type(self).__name__} <{hex(id(self))}> in state {self.state}{docstr}'

class _Defaults():
    '''stores all the default values, and has descriptions for them.

    Also provided here:
        default_properties stores a list of the relevant property names.
        self.help(property_name) tells the docstring for that property.
        self.update(new_defaults) allows to update the default values.
    '''
    # note: default_properties is attached to the class after defining it,
    # so that all the properties will be recorded before copying the list.

    def __repr__(self):
        result = (f'{type(self).__name__} instance containing {len(self.default_properties)} default values.\n'
                  'Use obj.help() or print(obj) for more info.')
        return result

    def update(self, other_defaults):
        '''updates self using values in other_defaults.
        other_defaults: dict or _Defaults.
            dict --> set self.key=value in self for (key, value) in dict items.
            _Defaults --> replace all default_properties values in self with those in other_defaults.
        '''
        for prop in self.default_properties:
            try:
                val = getattr(other_defaults, prop)
            except AttributeError:
                pass
            else:
                setattr(self, prop, val)

    def _get_prop_object(self, property_name):
        '''gets the property object associated with property name, from type(self).
        raise AttributeError and print available properties if property_name is not found.
        '''
        cls = type(self)
        try:
            prop = getattr(cls, property_name)
        except AttributeError:
            print(f'Error, property "{property_name}" not found (for object of type {cls}).')
            print(f'Available properties are: {self.default_properties}')
            raise
        return prop

    def _prop_readonly_str(self, property_name):
        '''returns '' if property is writable, else " (read-only)".'''
        return ' (read-only)' if self._get_prop_object(property_name).fset is None else ''

    def _help_prop_str(self, property_name):
        '''returns property_name's doc string, formatted nicely.'''
        return getdoc(self._get_prop_object(property_name))

    def _tab_str(self):
        '''returns self.STRINGREP_TAB if available, else 4 spaces.'''
        return getattr(self, 'STRINGREP_TAB', ' '*4)

    def help(self, property_name=None, as_string=False):
        '''print docs for property_name, or all properties in self.default_properties.
        if as_string, return string instead.
        '''
        if property_name is None:
            header = (f'Help on instance of {type(self)}.\n'
                      'Contains properties (access via obj.PROPNAME; set via obj.PROPNAME = value):\n\n')
            props_help = tuple(self.help(prop, as_string=True) for prop in self.default_properties)
            result = header + '\n\n'.join(props_help)
        else:
            result = (f'{repr(property_name)}{self._prop_readonly_str(property_name)}:\n'
                      f'{indent(self._help_prop_str(property_name), self._tab_str())}')
        if as_string:
            return result
        else:
            print(result)

default_properties = []   # list which will store all the properties in the _Defaults class.

def _attach_prop(name, doc=None, fget=None, fset=None, fdel=None):
    '''sets default property named name for the _Defaults class.'''
    default_properties.append(name)
    setattr(_Defaults, name, property(fget=fget, fset=fset, fdel=fdel, doc=doc))

def _attach_attr_prop(name, store, attr, doc=None):
    '''sets default property named name for the _Defaults class. Uses basic fget & fset:
    fget = lambda self: getattr(store, attr);
    fset = lambda self, value: setattr(store, attr, value).
    '''
    return _attach_prop(name, doc=doc,
                fget = lambda self: getattr(store, attr),
                fset = lambda self, value: setattr(store, attr, value))

def _attach_onoff_prop(name, store, doc=None):
    '''sets default property named name for the _Defaults class. Assumes store is an OnOffSwitch.
    sets doc, fget, and fset appropriately:
    doc = store.doc if doc is None else doc
    fget = lambda self: store
    fset = lambda self, value: store.set(value)
    '''
    return _attach_prop(name, doc=store.doc if doc is None else doc,
                fget = lambda self: store,
                fset = lambda self, value: store.set(value))


''' ----------------------------- default values ----------------------------- '''
# the naming convention is to use ALL CAPS for a class containing default value(s),
# but lowercase for a pointer to an actual default value.

# note: OnOffSwitch instances *contain* a default value (which they return when evaluated as a bool)

# # # ---- "front-end" defaults ---- # # #
RENDER = EmptyClass()   # instance of EmptyClass built to hold render defaults info as attributes.
RENDER.MATH = OnOffSwitch(True, 'Whether to render math.')
_attach_onoff_prop('RENDER_MATH', RENDER.MATH)

RENDER.maxlen = 15000
_attach_attr_prop('RENDER_MAXLEN', RENDER, 'maxlen',
        '''if length of string is more than this many characters, don't render as math.
        Also settable via RENDER_MATH.maxlen.''')

RENDER.mode = 'math'
_attach_attr_prop('RENDER_MODE', RENDER, 'mode',
        '''how to render math. 'print', 'math', or 'latex'. See help(SymSolver.view) for details.''')

TIMEOUT = EmptyClass()   # instance of EmptyClass built to hold timeout info as attributes.
TIMEOUT.seconds = None
_attach_attr_prop('TIMEOUT_SECONDS', TIMEOUT, 'seconds',
        '''number of seconds before giving up on simplify or expand related ops.
        A value of None means "never timeout".''')

TIMEOUT.max_view_per_second = 100
_attach_attr_prop('TIMEOUT_MAX_VIEW_PER_SECOND', TIMEOUT, 'max_view_per_second',
        '''number of times it is okay to call view() within 1 second.
        If called more frequently, view() will print() instead of IPython.display().
        (Equivalent: remember the calltime for up to this many of the most-recent calls to view;
        print() instead of display() if the earliest-remembered-calltime is less than 1 second ago.)''')

TIMEOUT.WARNINGS = OnOffSwitch(True, 'Whether to make a warning when timeout occurs.')
_attach_onoff_prop('TIMEOUT_WARNINGS', TIMEOUT.WARNINGS)

STRINGREP = EmptyClass()  # instance of EmptyClass built to hold string rep info as attributes.
STRINGREP.tab = ' '*4
_attach_attr_prop('STRINGREP_TAB', STRINGREP, 'tab',
        '''default string to use as 'tab', e.g. when formatting text calls for using an 'indent'.''')

STRINGREP.fraction_layers = 1
_attach_attr_prop('STRINGREP_FRACTION_LAYERS', STRINGREP, 'fraction_layers',
        '''number of layers of fractions allowed when getting string representations of SymbolicObjects.
        Beyond this many layers, just use exponentiation by a negative number, instead of showing a fraction.

        Number of fraction layers can be controlled for each call to _str(), __str__(), or view() routines,
        via the fraction_layers kwarg.''')

STRINGREP.numbers_precision = 5
_attach_attr_prop('STRINGREP_NUMBERS_PRECISION', STRINGREP, 'numbers_precision',
        '''number of digits of precision in string representations of numbers.
        Goes directly into format(s, '.Ng'). E.g. 5 --> format(s, '.5g').''')

STRINGREP.array_precision = 3
_attach_attr_prop('STRINGREP_ARRAY_PRECISION', STRINGREP, 'array_precision',
        '''number of digits of precision in string representation of min, mean, max for array,
        when using "short string" version of array which shows min, mean, max, and shape.''')

STRINGREP.ARRAY_ANNOTATE = OnOffSwitch(True, "Whether to put words in pretty array str.")
_attach_onoff_prop('STRINGREP_ARRAY_ANNOTATE', STRINGREP.ARRAY_ANNOTATE)

STRINGREP.ARRAY_NANMEAN = OnOffSwitch(True, "Whether to use 'nan' funcs for pretty array str.")
_attach_onoff_prop('STRINGREP_ARRAY_NANMEAN', STRINGREP.ARRAY_NANMEAN,
        '''Whether to use 'nan' funcs for pretty array str.
        True --> use np.nanmin, np.nanmean, np.nanmax.
        False --> use np.min, np.mean, np.max.''')

STRINGREP.array_smallsize = 5
_attach_attr_prop('STRINGREP_ARRAY_SMALLSIZE', STRINGREP, 'array_smallsize',
        '''if array size is this number or smaller, show all array elements instead of a summary.''')

PROGRESS_UPDATES = EmptyClass()  # instance of EmptyClass built to hold progress update routine defaults as attributes.
PROGRESS_UPDATES.print_freq = 2
_attach_attr_prop('PROGRESS_UPDATES_PRINT_FREQ', PROGRESS_UPDATES, 'print_freq',
        '''Minimum time [in seconds] between progress update print statements.''')

COMPONENTS = EmptyClass()  # instance of EmptyClass built to hold vector component routine defaults as attributes.
COMPONENTS.basis = None
_attach_attr_prop('COMPONENTS_BASIS', COMPONENTS, 'basis',
        '''default Basis to use during componentize() routines.
        If None, basis must be provided directly to those routines when called.''')

COMPONENTS.ndim = None
_attach_attr_prop('COMPONENTS_NDIM', COMPONENTS, 'ndim',
        '''default number of dimensions associated with one vector;
        only used during routines that require knowledge about number of dimensions in a vector.

        If None, those routines will try using len(DEFAULTS.COMPONENTS_BASIS), if possible.
        If still unknown, those routines will require that ndim info be entered as input.

        ndim can also be controlled directly on a per-call basis, usually via the 'ndim' kwarg.''')

COMPONENTS.SHORTHAND = OnOffSwitch(True, 'Whether to use shorthand for DotProducts with a basis vector.')
_attach_prop('COMPONENTS_SHORTHAND',  # using basic _attach_prop due to custom setter function.
        r'''whether to (by default) use shorthand for DotProduct objects involving an OrthonormalBasis vector.
        E.g. if using shorthand, convert \vec{u} dot xhat --> u_x, if xhat is in an OrthonormalBasis.

        Whether to use shorthand can also be controlled directly on a per-call basis, via:
            - the 'shorthand' kwarg, for each call to componentize() or component().
            - the 'components_shorthand' kwarg, during a call of simplify(),
                to enable/disable the shorthand simplification routine.''',
        lambda self: COMPONENTS.SHORTHAND,
        lambda self, value: COMPONENTS._shorthand_setter(self, value),  # defined in back-end defaults, below.
        )

COMPONENTS.if_missing_metric = 'crash'
_attach_attr_prop('COMPONENTS_IF_MISSING_METRIC', COMPONENTS, 'if_missing_metric',
        '''how to behave if a "skippable" operation requires a metric, but receives None.
        E.g. if obj.componentize(basis) requires basis.metric but it is undefined,
        reasonable behaviors include "crash with appropriate error" or "return obj with no changes."
        Options provided here:
            'crash' --> crash; raise MetricUndefinedError.
            'warn' --> warnings.warn(repr(error that would have been raised if in 'crash' mode))
            'ignore' --> fail silently.''')

POLYROOTS = EmptyClass()  # instance of EmptyClass built to hold Polynomial root finding defaults as attributes.
POLYROOTS.mode = 'numpy'
_attach_attr_prop('POLYROOTS_MODE', POLYROOTS, 'mode',
        '''how to calculate polynomial roots, by default. Options:
        'numpy' or 'np' --> use numpy.polynomial.Polynomial.roots
        'mpmath' or 'mpm' --> use mpmath.polyroots''')

POLYROOTS.extraprec = 20
_attach_attr_prop('POLYROOTS_EXTRAPREC', POLYROOTS, 'extraprec',
        '''default value of 'extraprec' to use during mpmath.polyroots.''')

POLYROOTS.EASYCHECK = OnOffSwitch(True, "Whether to test for easy roots (e.g. quadratic formula) before root-finding.")
_attach_onoff_prop('POLYROOTS_EASYCHECK', POLYROOTS.EASYCHECK)

POLYROOTS.LINALG_ERRORS_OK = OnOffSwitch(True, "Whether to allow numpy.linalg.LinAlgError while finding roots.")
_attach_onoff_prop('POLYROOTS_LINALG_ERRORS_OK', POLYROOTS.LINALG_ERRORS_OK,
        '''Whether to allow numpy.linalg.LinAlgError while finding roots.
        if True, use PolyMPArray.RESULT_MISSING (default: nan + 1j nan) instead of raising linalg error.''')

POLYROOTS.MONICIZE = OnOffSwitch(True, "Whether to divide by largest-degree coefficient before root-finding.")
_attach_onoff_prop('POLYROOTS_MONICIZE', POLYROOTS.MONICIZE)

POLYFRACTION = EmptyClass()  # instance of EmptyClass built to hold PolyFraction routine defaults as attributes.
POLYFRACTION.careful_roots_mode = 'deval'
_attach_attr_prop('POLYFRACTION_CAREFUL_ROOTS_MODE', POLYFRACTION, 'careful_roots_mode',
        '''tells how to be careful about roots of PolyFraction pf. Tells when to reject roots (from numerator):
        'deval' --> reject root if denom(root) is close to 0.
            i.e., reject if |denom(root)| < denom.error_scale(root) * 1/tol.
        'evaluate' --> reject root if pf(root) is not close to 0.
            i.e., reject if |pf(root)| > tol.
        'matching' --> reject if something close to root is found in denom.roots().
            i.e., reject if any(np.isclose(dr, root, rtol=tol[0], atol=tol[1]) for dr in denom.roots()).''')

POLYFRACTION._roots_dtol = 1e-3
_attach_attr_prop('POLYFRACTION_ROOTS_DTOL', POLYFRACTION, '_roots_dtol',
        '''tolerance for "BAD" root of PolyFraction object pf, when using careful='deval'.
        root is "BAD" if |pf.denom(root)| < pf.denom.error_scale(root) / _roots_dtol.
        Recommend _roots_dtol<=1e-1 for safety; default 1e-3. Certainly shouldn't use _roots_dtol>1.''')
        # divide by _roots_dtol, to follow the convention: larger tolerance --> accept more roots.

POLYFRACTION._roots_tol = 1e-2
_attach_attr_prop('POLYFRACTION_ROOTS_TOL', POLYFRACTION, '_roots_tol',
        '''tolerance for what counts as a "BAD" root when finding roots of PolyFraction object.
        root is "BAD" if |pf(root)| > _roots_tol.''')

POLYFRACTION._roots_ratol = (1e-9, 1e-16)
_attach_attr_prop('POLYFRACTION_ROOTS_RATOL', POLYFRACTION, '_roots_ratol',
        '''relative and absolute tolerances for what counts as a "MATCH" when finding roots of PolyFraction.
        This applies when using "matching" mode for careful root finding;
        in this mode, compare root of numerator directly to roots of denominator,
        rejecting roots of numerator when a match is found.
        compares via np.isclose(denom_root, numer_root, rtol=tol[0], atol=tol[1]).''')

NUMBERS = EmptyClass()  # instance of EmptyClass built to hold defaults for the numbers subpackage.
NUMBERS.imaginary_unit_str = 'i'
_attach_attr_prop('IMAGINARY_UNIT_STR', NUMBERS, 'imaginary_unit_str',
        '''string to use when showing the imaginary unit.''')

NUMBERS.RATIONAL_TO_FLOAT = OnOffSwitch(True, 'Whether to convert SymSolver.Rational objects to floats during math.')
_attach_onoff_prop('RATIONAL_TO_FLOAT', NUMBERS.RATIONAL_TO_FLOAT,
        '''whether to convert SymSolver.Rational objects to floats during math if necessary.
        ("necessary" <--> doing math with a Rational and a non-symbolic-object number.
        There's no problem if doing math between two Rationals, or a Rational and a SymbolicObject.)

        If False, instead default to implementation from AbstractOperation, if it exists, else crash.
        For example, during Rational(7,4) * 0.1:
            True -->  0.175
            False --> Product(Rational(7, 4), 0.1)
        For example, during Rational(7,4) > 0.1:
            True --> 1.75 > 0.1 --> True
            False --> 0.1 < Rational(7,4) --> TypeError  (because float.__lt__(Rational(...)) not implemented)''')

SYMBOLS = EmptyClass()  # instance of EmptyClass built to hold defaults related to Symbols subpackage.
SYMBOLS.o0_CONSTANT = OnOffSwitch(True, 'Whether to use constant=True by default for Symbols with order 0.')
_attach_onoff_prop('SYMBOLS_o0_CONSTANT', SYMBOLS.o0_CONSTANT)

SYMBOLS.new_str = 'S'
_attach_attr_prop('NEW_SYMBOL_STR', SYMBOLS, 'new_str',
        '''The default symbol string to use for s when making a new Symbol if s is not required.
        E.g. during new_unique_symbol() or new_symbol_like().
        Note: s is required by most common ways of making a new symbol.
        E.g. user should use symbol(...) and in that method s must be provided.''')

ESSENCES = EmptyClass()  # instance of EmptyClass built to hold defaults for the essences subpackage.
ESSENCES.symbol_str = 'E'
_attach_attr_prop('ESSENCES_SYMBOL_STR', ESSENCES, 'symbol_str',
        '''The default symbol string to use when making a new essence symbol, e.g. during essentialize().''')

PATTERNS = EmptyClass()  # instance of EmptyClass built to hold defaults for patterns (see essences subpackage).
PATTERNS.symbol_str = 'C'
_attach_attr_prop('PATTERN_SYMBOL_STR', PATTERNS, 'symbol_str',
        '''The default symbol string to use when making a new PatternSymbol.''')

PATTERNS.match_any = ['s', 'subscripts', 'constant', 'hat', 'order', 'targets', 'id_']
_attach_attr_prop('PATTERN_MATCH_ANY', PATTERNS, 'match_any',
        '''The default _EQ_TEST_ATTRS to ignore during pattern matching for PatternSymbols.
        E.g. if 's' is in this list, then pattern matching doesn't require matching to pattern_symbol.s.

        For an individual PatternSymbol, can require matching more or fewer things,
        via kwargs 'match_any' and 'must_match'.''')

PATTERNS._any_symbol_str = 'A'
_attach_attr_prop('PATTERN__ANY_SYMBOL_STR', PATTERNS, '_any_symbol_str',
        '''Suggested symbol string for new PatternSymbols built to match anything.''')

PATTERNS._scalar_symbol_str = 'S'
_attach_attr_prop('PATTERN__SCALAR_SYMBOL_STR', PATTERNS, '_scalar_symbol_str',
        '''Suggested symbol string for new PatternSymbols built to match scalars.''')

PATTERNS._vector_symbol_str = 'V'
_attach_attr_prop('PATTERN__VECTOR_SYMBOL_STR', PATTERNS, '_vector_symbol_str',
        '''Suggested vector string for new PatternSymbols built to match vectors.''')

SOLVING = EmptyClass()  # instance of EmptyClass built to hold defaults for solving equations / systems.
SOLVING.simplify_after = True  # note: intentionally NOT an OnOffSwitch; user might set a dict here.
_attach_attr_prop('SOLVING_SIMPLIFY_AFTER', SOLVING, 'simplify_after',
        '''whether to call result.simplify() during equation_object.solve(...) (or .eliminate(...)),
        Note: this default does not apply to individual methods such as vecsolve or linear_eliminate.
        if set to a dict, use this as the kwargs for simplify().''')

SOLVING.system_simplify_mode = 'simplified' #('essentialize', 'simplify', 'expand', 'simplify', 'essentialize')
_attach_attr_prop('SOLVING_SYSTEM_SIMPLIFY_MODE', SOLVING, 'system_simplify_mode',
        '''str, bool, or tuple indicating how to simplify system after each solvestep.
        'essentialize' --> self._essentialize();
        'simplify', 'expand', 'simplified' --> self.system.(that method)();
        True --> self.system.simplify(); False --> don't simplify at all;
        tuple --> values must be options above; apply each in turn.''')

UNITS = EmptyClass()  # instance of EmptyClass built to hold defaults for units.
UNITS.simplify_shorthands = OnOffSwitch(True, 'Whether to simplify results from UnitsShorthand')
_attach_onoff_prop('UNITS_SIMPLIFY_SHORTHANDS', UNITS, 'simplify_shorthands')


# # # ---- "back-end" defaults ---- # # #
# ZERO and ONE are provided for checking 'is' with 0 and 1.
# note that 'is' might provide false negatives when comparing with integers;
# equal integers are not guaranteed to be the same object (e.g. int(1000.0) is not 1000).
# however 'is' will never provide false positives. So it is nice to have sometimes, for efficiency.
ZERO = 0
ONE = 1
MINUS_ONE = -ONE
_attach_prop('ZERO', '''the number 0''', lambda self: ZERO)
_attach_prop('ONE', '''the number 1''', lambda self: ONE)
_attach_prop('MINUS_ONE', '''the number -1''', lambda self: MINUS_ONE)

TRACEBACKHIDE = OnOffSwitch(True, 'Whether to hide some internal function from python error tracebacks.')
_attach_onoff_prop('TRACEBACKHIDE', TRACEBACKHIDE)

DEBUG = OnOffSwitch(False, 'Can enable & use while debugging. By default does nothing even when enabled.')
_attach_onoff_prop('DEBUG', DEBUG,
        '''Can enable & use while debugging. By default does nothing even when enabled.

        Example use-case:
            x = 1           # << works fine
            for i in range(100):
                x = foo(x)  # << works fine
            y = foo(2*x)    # << behaves unexpectedly, not sure why.
        Instead of making foo() always do debugging print statements,
        can put in foo:
            if DEFAULTS.DEBUG: <code to make debugging print statements, or raise Exception>
        Then, can edit the code so it says:
            x = 1
            for i in range(100):
                x = foo(x)
            DEFAULTS.DEBUG = True  # << new code
            y = foo(2*x)    # << now foo will do debugging prints, or raise Exception.
        then can see the debugging prints only when relevant,
        or get the crash only when relevant (so you can use pdb.pm() to debug post-mortem).''')

DEBUG_ = EmptyClass()  # instance of EmptyClass built to hold defaults for debugging
DEBUG_.CONSTANTS = OnOffSwitch(False, "Whether to add subscripts when viewing symbols with non-None is_constant().")
_attach_onoff_prop('DEBUG_CONSTANTS', DEBUG_.CONSTANTS,
        '''Whether to add subscripts when viewing symbols with non-None is_constant().
        if True, use '(C)' for is_constant=True, '(V)' for is_constant=False.''')

DEBUG_.UNITS = OnOffSwitch(False, "Whether to add units_base to repr for symbols.")
_attach_onoff_prop('DEBUG_UNITS', DEBUG_.UNITS)

DEBUG_.LINEARIZING = OnOffSwitch(False, "Whether to put (*) for MIXED_ORDER symbols.")
_attach_onoff_prop('DEBUG_LINEARIZING', DEBUG_.LINEARIZING)

DEBUG_.CANONICAL_ORDER = OnOffSwitch(False, 'Whether to warnings.warn(...) when canonical order non-unique.')
_attach_onoff_prop('DEBUG_CANONICAL_ORDER', DEBUG_.CANONICAL_ORDER)

CACHING = EmptyClass()  # instance of EmptyClass built to hold defaults for caching.
CACHING.maxlen = None
_attach_attr_prop('CACHING_MAXLEN', CACHING, 'maxlen',
        '''default max length for a cache for a single object. (None --> no maximum).
        Cache "length" is the number of values stored in cache (e.g. if results depend on inputs).''')

CACHING.OPS = OnOffSwitch(True, 'Whether to do caching of simplify() or expand() -related ops.')
_attach_onoff_prop('CACHING_OPS', CACHING.OPS,
        '''whether to do caching of simplify() or expand() -related ops.
        testing shows: faster when ON.''')

CACHING.CD = OnOffSwitch(True, 'Whether to do caching of contains_deep and contains_deep_subscript.')
_attach_onoff_prop('CACHING_CD', CACHING.CD,
        '''whether to do caching of contains_deep and contains_deep_subscript.
        testing shows: faster when ON.''')

CACHING.CD.maxlen = None
_attach_attr_prop('CACHING_CD_MAXLEN', CACHING.CD, 'maxlen',
        '''max length of cache (for contains_deep) for a single object. (None --> no maximum).''')

CACHING.EQ = OnOffSwitch(False, 'Whether to do caching for equals.')
_attach_onoff_prop('CACHING_EQ', CACHING.EQ,
        '''whether to do caching for equals.
        testing shows: faster when OFF.''')

CACHING.EQ.maxlen = 10
_attach_attr_prop('CACHING_EQ_MAXLEN', CACHING.EQ, 'maxlen',
        '''max length of cache (for equals) for a single object, if CACHING_EQ is enabled.''')

CACHING_PROPERTIES = OnOffSwitch(True, 'Whether to do caching for simple methods, e.g. is_constant, _equals0.')
_attach_onoff_prop('CACHING_PROPERTIES', CACHING_PROPERTIES,
        '''whether to do caching for simple methods e.g. is_constant, _equals0.
        "Simple" meaning the result depends only on the object, not any other inputs.''')

COMPONENTS._shorthand_setter = lambda self, value: COMPONENTS.SHORTHAND.set(value)
_attach_prop('_COMPONENTS_SHORTHAND_SETTER',
        '''setter function for COMPONENTS.SHORTHAND.
        we expose this interface so that subpackage(s) can attach more functionality.
        In particular, vectors.componentize.py adjusts this method so that it will
        also set "DO (or DON'T) skip components_shorthand simplification by default" appropriately.''',
        lambda self: COMPONENTS._shorthand_setter,
        lambda self, value: setattr(COMPONENTS, '_shorthand_setter', value),
        )

IMPORT_FAILURE_WARNINGS = OnOffSwitch(True, 'Whether to warnings.warn(...) when an optional import fails.')
_attach_onoff_prop('IMPORT_FAILURE_WARNINGS', IMPORT_FAILURE_WARNINGS,
        '''whether to warnings.warn(...) when an optional import fails while loading SymSolver packages.
        (If False, import may fail silently, but make verbose error whenever attempting to use the module.)''')


''' ----------------------------- finishing up, and defining DEFAULTS ----------------------------- '''
        
_Defaults.default_properties = default_properties.copy()

DEFAULTS = _Defaults()