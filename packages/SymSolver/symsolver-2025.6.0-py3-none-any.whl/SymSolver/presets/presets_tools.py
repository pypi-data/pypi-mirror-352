"""
File Purpose: misc. tools for presets
"""
from ..errors import InputError, InputMissingError, InputConflictError
from ..tools import viewdict

PRESETS = dict()  # << all currently-known pre-defined variables / equations / other objects.
PRESET_KINDS = dict()  # << map from "kind" to list of Presets for that kind.

def get_presets(requests, _to_list_if_only_one=False):
    '''returns a list of the requested preset values.
    requests: str or iterable
        str --> iterate through requests.split(' ')
        iterable --> for each request, get PRESETS[request]
    _to_list_if_only_one: bool, default False
        when there is only one request, this tells whether to return list or single result.
        e.g. get_presets('n', False) --> Symbol('n');  get_presets('n', True) --> [Symbol('n')]
    '''
    if isinstance(requests, str):
        requests = requests.split(' ')
    result = []
    for request in requests:
        try:  # << put in a try..except in order to raise a more verbose error if key is invalid.
            preset = PRESETS[request]
        except KeyError:
            errmsg = f"Preset not defined: {repr(request)}. See SymSolver.PRESETS for all available presets."
            raise NotImplementedError(errmsg) from None
        result.append(preset)
    if not _to_list_if_only_one and len(result) == 1:
        return result[0]
    return result

class Presets():
    r'''presets, setting, and kind, managed by one object.
    See also: load_presets, get_presets
    
    Example:
        PS = Presets('MISC')
        @PS.creator
        def define_presets():

            i = IUNIT    = ImaginaryUnit()
            e,           = symbols(('e',), constant=True)
            phi, theta   = symbols((r'\phi', r'\theta'))

            PS.set('i e IUNIT phi theta', globals())

        # elsewhere, can get all the 'MISC' presets via:
        load_presets('MISC')
    '''
    def __init__(self, *kinds):
        if len(kinds) == 0:
            raise InputMissingError('must input at least one kind')
        kinds = tuple(kind.upper() for kind in kinds)
        self.kinds = kinds
        for kind in kinds:
            PRESET_KINDS.setdefault(kind, []).append(self)
        self._creator = None
        self.presets = None

    def __repr__(self):
        return f'{type(self).__name__}(kinds={repr(self.kinds)})'

    def loaded(self):
        '''returns whether presets have been loaded for self, i.e. whether self.presets is not None'''
        return self.presets is not None

    def creator(self, f):
        '''tell self that f is the function used to create the associated presets.
        f should return a dict of presets.
        if this is called multiple times, raise InputConflictError
        '''
        if self._creator is not None:
            raise InputConflictError(f'{self}._creator was previously defined.')
        self._creator = f

    def get(self):
        '''returns self.presets. if self.presets not found, first call self._creator.
        raise InputMissingError if self._creator hasn't been defined.
        raise InputError if self.presets haven't been defined after calling self._creator.
        '''
        if not self.loaded():
            # need to get presets
            if self._creator is None:
                raise InputMissingError(f'Cannot determine presets from {self} with no _creator.')
            self._creator()
            if not self.loaded():
                errmsg = f'{self}._creator did not define self.presets. Probably forgot {{self}}.set(...)'
                raise InputError(errmsg)
        return self.presets

    def __call__(self):
        '''returns self.presets, calling self._creator if needed. Equivalent to self.get().'''
        return self.get()

    def set(self, keys, source):
        '''sets keys in PRESETS to values from source.
        keys: str or iterable
            str --> iterate through keys.split(' ')
            iterable --> for each key, get source[key]
        source: dict
            mapping from keys to values.
            probably locals() of wherever this is called.

        returns a dict with just the keys listed here.
        also sets updates self.presets using result.

        example:
            presetter = Presets('iXYZ')
            X, Y, Z = symbols(('x', 'y', 'z'))
            i = ImaginaryUnit()
            presetter.set(('i', 'X', 'Y', 'Z'), locals())

            # check the result:
            presetter() --> {'i': i, 'X': X, 'Y': Y, 'Z': Z}
        '''
        if isinstance(keys, str):
            keys = keys.split(' ')
        result = dict()
        for key in keys:
            val = source[key]
            PRESETS[key] = val
            result[key] = val
        if self.presets is None:
            self.presets = dict()
        self.presets.update(result)
        return result


def load_presets(*kinds, skip=[], dst=None):
    '''loads these kinds of presets (put into PRESETS; also put into dst if provided).
    For example, to make variables accessible directly, use dst=locals().

    kinds are case-insensitive (will be internally converted to UPPERCASE).
    "kind" options are given by PRESET_KINDS.keys()
    if no kinds are provided, will load ALL presets.
    if any kinds are invalid, raise KeyError before loading any presets.

    After loading presets, can also use get_presets to access them.

    skip: list or str
        if provided, skip loading any Presets which appear in any of the kinds in skip.
        if single string, use skip=[skip] instead.
        note: if any presets not in skip load a kind in skip, this won't prevent that.
            E.g. the code which loads kind='FLUIDS' also happens to load kind='FLUID_VARS',
            so load_presets('FLUIDS', skip=['FLUID_VARS']) will still end up loading FLUID_VARS.
    
    returns dict of all presets of these kinds.
    '''
    # ensure all kinds exist.
    kinds = [kind.upper() for kind in kinds]
    if len(kinds) == 0:
        kinds = list(PRESET_KINDS.keys())
    else:
        for kind in kinds:
            if kind not in PRESET_KINDS:
                raise KeyError(f'Unknown preset kind: {repr(kind)}')
    if isinstance(skip, str):
        skip = [skip]
    for kind in skip:
        if kind not in PRESET_KINDS:
            raise KeyError(f'Unknown preset kind (in skip): {repr(kind)}')
    # get list of Presets to load, skipping any which appear in any skip
    to_consider = [ps for kind in kinds for ps in PRESET_KINDS[kind]]
    to_skip = {id(ps): True for skind in skip for ps in PRESET_KINDS[skind]}
    to_load = [ps for ps in to_consider if not to_skip.get(id(ps), False)]
    # load the presets
    result = viewdict()
    for ps in to_load:
        result.update(ps.get())
    # update dst if necessary, then return.
    if dst is not None:
        dst.update(result)
    return result
