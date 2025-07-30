"""
File Purpose: PowerLite, ProductLite, SumLite
"""

from .basics_tools import (
    get_base_and_power, get_factors, get_summands,
)
from .power import Power
from ..abstracts import contains_deep, ComplexityBinning
from ..tools import (
    min_number, int_equals,
    weakref_property_simple,
    Binding,
)
from ..initializers import INITIALIZERS

from ..defaults import ZERO

binding = Binding(locals())


''' --------------------- Lites --------------------- '''

class PowerLite():
    '''lightweight "power" used for internal methods.
    original=None if original Power unknown, else original Power.'''
    def __init__(self, base, exp, original=None, *, prodl=None):
        self._base = base
        self._exp = exp
        self._original = original
        self.prodl = prodl

    prodl = weakref_property_simple('_prodl',
            doc='''the ProductLite from which self was created. prodl.original=None if self.original is changed.''')
    original = property(lambda self: self._original, doc='''original Power(base, exp)''')
    @original.setter
    def original(self, value):
        prodl = self.prodl
        if prodl is not None:
            prodl.original = None
        self._original = value
    base = property(lambda self: self._base, doc='''base from original Power(base, exp)''')
    @base.setter
    def base(self, value):
        self.original = None
        self._base = value
    exp = property(lambda self: self._exp, doc='''exp from original Power(base, exp)''')
    @exp.setter
    def exp(self, value):
        self.original = None
        self._exp = value

    @classmethod
    def from_term(cls, x, *, polys=[]):
        '''create PowerLite from x. x can be a Power, other SymbolicObject, or other object.
        x will be saved in self.original.
        if x base in polys (via 'is'), result base will be x and exp will be 1, regardless of x.
        '''
        base, exp = get_base_and_power(x)
        if any(base is poly for poly in polys):
            return cls(x, 1, original=x)
        else:
            return cls(base, exp, original=x)

    def __repr__(self):
        return f'{type(self).__name__}({self.base}, {self.exp})'

    def __iter__(self):
        yield self.base
        yield self.exp


class ProductLite(dict):
    '''lightweight "product" used for internal methods.
    {i: PowerLite.from_term(factor)} for factor in the original product.
    original=None if original Product unknown, else original Product.
    '''
    def __init__(self, *args, original=None, suml=None, **kw):
        super().__init__(*args, **kw)
        for factor in self.values():
            factor.prodl = self
        self._original = original
        self.suml = suml
        self._nextkey = 0 if len(self)==0 else (1 + max(self.keys()))

    def _new(self, *args, **kw):
        return type(self)(*args, **kw)

    suml = weakref_property_simple('_suml',
            doc='''the SumLite from which self was created. suml.original=None if self.original is changed.''')
    original = property(lambda self: self._original, doc='''original Power(base, exp)''')
    @original.setter
    def original(self, value):
        '''tell parent that self.original is no longer valid'''
        suml = self.suml
        if suml is not None:
            suml.original = None
        self._original = value

    def copy(self):
        result = super().copy()
        return self._new(result, original=self.original, suml=self.suml)

    @classmethod
    def from_term(cls, x, *, polys=[], **kw__get_factors):
        '''create ProductLite from a "math object". x will be saved in self.original.
        if x base in polys (via 'is'), PowerLite base will be x and exp will be 1, regardless of x.
        '''
        i_factors = {i: PowerLite.from_term(factor, polys=polys)
                        for i, factor in enumerate(get_factors(x, **kw__get_factors))}
        return cls(i_factors, original=x)

    @classmethod
    def from_list(cls, flist, *, polys=[]):
        '''create ProductLite from list of factors.'''
        i_factors = {i: PowerLite.from_term(factor, polys=polys) for i, factor in enumerate(flist)}
        return cls(i_factors)

    @classmethod
    def from_lites(cls, power_lites):
        '''create ProductLite from list of PowerLite objects'''
        i_factors = {i: powl for i, powl in enumerate(power_lites)}
        return cls(i_factors)

    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

    def __setitem__(self, key, val):
        self.original = None
        if key >= self._nextkey:
            self._nextkey = self._nextkey + 1
        super().__setitem__(key, val)


class SumLite(dict):
    '''lightweight "sum" used for internal methods.
    {i: ProductLite.from_term(summand)} for summand in the original sum.
    original=None if original Sum unknown, else original Sum.
    compress: if True, self.compress() after initializing.
    '''
    def __init__(self, *args, original=None, compress=True, **kw):
        super().__init__(*args, **kw)
        for factor in self.values():
            factor.suml = self
        self.original = original
        self._nextkey = 0 if len(self)==0 else (1 + max(self.keys()))
        if compress:
            self.compress()

    def _new(self, *args, **kw):
        return type(self)(*args, **kw)

    def copy(self):
        result = super().copy()
        return self._new(result, original=self.original)

    def product_copy(self):
        '''returns copy of self & also replacing ProductLites with copies.'''
        result = super().copy()
        for i, prodl in result.items():
            result[i] = prodl.copy()
        return self._new(result, original=self.original)

    @classmethod
    def from_term(cls, x, *, compress=True, **kw):
        '''create SumLite from x. x can be a list of summands or a Sum.
        x will be saved in self.original.
        compress gets passed to cls().
        other kwargs go to ProductLite.from_term.
        '''
        i_summands = {i: ProductLite.from_term(summand, **kw) for i, summand in enumerate(get_summands(x))}
        return cls(i_summands, original=x, compress=compress)

    @classmethod
    def from_list(cls, slist, *, compress=True, **kw):
        '''create SumLite from list of summands. compress gets passed to cls().'''
        i_summands = {i: ProductLite.from_term(summand, **kw) for i, summand in enumerate(slist)}
        return cls(i_summands, compress=compress)

    @classmethod
    def from_lites(cls, product_lites, *, compress=True):
        '''create SumLite from list of ProductLite objects. compress gets passed to cls().'''
        i_summands = {i: prodl for i, prodl in enumerate(product_lites)}
        return cls(i_summands, compress=compress)

    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

    def __setitem__(self, key, val):
        self.original = None
        if key >= self._nextkey:
            self._nextkey = self._nextkey + 1
        super().__setitem__(key, val)

    def flat(self):
        '''yield (i, j, powerlite_ij) from self, where self[i][j] == powerlite'''
        for i, prodl in self.items():
            for j, powl in prodl.items():
                yield i, j, powl

    def bases(self):
        '''returns {id(base): base} for base in self.'''
        return {id(base): base for i, j, (base, exp) in self.flat()}

    def bases_indices(self):
        '''returns {id(base): list of pairs (i,j) where base occurs in self}.'''
        result = dict()
        for (i, j, powl) in self.flat():
            base = powl.base
            result.setdefault(id(base), []).append((i, j))
        return result

    def bases_and_indices(self):
        '''returns {id(base): (base, list of pairs (i,j) where base occurs in self)}.'''
        result = dict()
        for (i, j, powl) in self.flat():
            base = powl.base
            id_ = id(base)
            try:
                result[id_][1].append((i, j))
            except KeyError:
                result[id_] = (base, [(i, j)])
        return result

    def bases_and_i_to_j(self, polys=[]):
        '''returns {id(base): (base, {i: j such that base occurs at self[i][j]}) }.
        if len(polys) > 0, return self.bases_and_i_to_j_polymode(polys) instead.
        '''
        if len(polys) > 0:
            return self.bases_and_i_to_j_polymode(polys)
        result = dict()
        for (i, j, powl) in self.flat():
            base = powl.base
            id_ = id(base)
            try:
                idict = result[id_][1]
            except KeyError:
                result[id_] = (base, {i: j})
            else:
                idict[i] = j
        return result

    def i_to_has_poly(self, polys=[]):
        '''returns dict of {i: {j: poly such that self[i][j].base.contains_deep(poly)} (for any poly in polys)}.
        You can learn if self[i] has poly via bool(result[i]). Or via len(result[i])>0.
        '''
        result = {i: {j: poly
                        for j, (base, exp) in prodl.items()
                        for poly in polys
                            if contains_deep(base, poly)}
                    for i, prodl in self.items()}
        return result

    def bases_and_i_to_j_polymode(self, polys):
        '''like bases_and_i_to_j but excludes non-poly bases from products with at least one poly.'''
        i_to_has_poly = self.i_to_has_poly(polys=polys)
        result = dict()
        for i, prodl in self.items():
            has_poly = i_to_has_poly[i]
            if has_poly:
                to_add = tuple((j, self[i][j]) for j, base in has_poly.items())
            else:
                to_add = tuple((j, base) for j, (base, powl) in prodl.items())
            for j, base in to_add:
                id_ = id(base)
                try:
                    idict = result[id_][1]
                except KeyError:
                    result[id_] = (base, {i: j})
                else:
                    idict[i] = j
        return result

    def min_power_from(self, indices, *, return_index=False):
        '''return minimum exp from all self[i][j] for (i,j) in indices.
        only tries numerical exponents; if all are non-numeric use the first exponent instead.
        if return_index, also return (i,j) where minimum occurs.
        '''
        indices = tuple(indices)
        exps = [self[i][j].exp for i, j in indices]
        result = min_number(exps, return_index=return_index)
        if return_index:
            min_power, i_internal = result
            min_index = indices[i_internal]
            return (min_power, min_index)
        else:
            return min_power

    def min_power_lite_from(self, indices):
        '''return the powerlite with the minimum exp from all self[i][j] for (i,j) in indices.
        only tries numerical exponents; if all are non-numeric use the first exponent instead.
        '''
        _power, index = self.min_power_from(indices, return_index=True)
        i, j = index
        return self[i][j]


''' --------------------- Pop / Append / Split / Index --------------------- '''

with binding.to(ProductLite):
    @binding
    def pop(self, key, **kw):
        self.original = None
        super(ProductLite, self).pop(key, **kw)

    @binding
    def append_term(self, x):
        '''append "math object" x to self'''
        self.append_lite(PowerLite.from_term(x))

    @binding
    def append_lite(self, powl):
        '''append PowerLite to self'''
        self[self._nextkey] = powl
        self.original = None

    @binding
    def appended_lite(self, powl):
        '''return copy of self with PowerLite appended to it'''
        result = self.copy()
        result.append_lite(powl)
        return result

with binding.to(SumLite):
    @binding
    def pop(self, key, **kw):
        self.original = None
        super(SumLite, self).pop(key, **kw)

    @binding
    def append_lite(self, prodl):
        '''append ProductLite to self'''
        self[self._nextkey] = prodl
        self.original = None

    @binding
    def appended_lite(self, prodl):
        '''return copy of self with ProductLite appended to it'''
        result = self.copy()
        result.append_lite(prodl)
        return resul

    @binding
    def append_term(self, x):
        '''append "math object" x to self'''
        self.append_lite(ProductLite.from_term(x))

    @binding
    def multi_index(self, idx):
        '''returns SumLite with [self[i] for i in idx]. if idx is None, return self.copy()'''
        return self.copy() if idx is None else self._new({i: self[i] for i in idx})

    @binding
    def keys_except(self, idx):
        '''returns keys in self which don't appear in idx. if idx is None, return empty list'''
        return tuple() if idx is None else tuple(set(self.keys()) - set(idx))

    @binding
    def split(self, idx=None):
        '''returns [self[i] for i in idx], [self[i] for i in self but not in idx].
        if idx is None, return self, empty SumLite.
        '''
        idx_not = self.keys_except(idx)
        return self.multi_index(idx), self.multi_index(idx_not)


''' --------------------- Multiply / Divide / Add power / Subtract power --------------------- '''

with binding.to(PowerLite):
    @binding
    def add_power(self, power):
        '''add power to self.exp'''
        self.exp = self.exp + power

    @binding
    def sub_power(self, power):
        '''subtract power from self.exp'''
        self.exp = self.exp - power

with binding.to(ProductLite):
    @binding
    def add_power(self, i, power):
        '''add power to the exponent of self[i].'''
        powl = self[i]
        powl.add_power(power)
        if int_equals(powl.exp, ZERO):
            self.pop(i)

    @binding
    def sub_power(self, i, power):
        '''subtract power from the exponent of self[i].'''
        powl = self[i]
        powl.sub_power(power)
        if int_equals(powl.exp, ZERO):
            self.pop(i)

with binding.to(SumLite):
    @binding
    def add_power(self, i, j, power):
        '''add power to the exponent of self[i][j]'''
        self[i].add_power(j, power)

    @binding
    def sub_power(self, i, j, power):
        '''subtract power from the exponent of self[i][j]'''
        self[i].sub_power(j, power)

    @binding
    def divide_min_power_from(self, ijdict):
        '''divides min exponent Power within (self[i][j] for (i,j) in ijdict) from (self[i] for i in ijdict).
        returns (PowerLite with minimum exponent, result of division, terms unaffected by this division)
        '''
        minpowl = self.min_power_lite_from(ijdict.items())
        divided, unaffected = self.divide_lite(minpowl, idx=ijdict.keys())
        return minpowl, divided, unaffected

    @binding
    def divide(self, x, idx=None):
        '''divide "math object" x from terms in self. (all terms if idx=None)
        NOTE: IN-PLACE OPERATION. i.e. the PowerLites inside self will be affected.
        idx: None or iterable
            None --> return self / powerlite
            iterable --> divide terms=[self[i] for i in idx] by powerlite.
                    return (those terms / powerlite), (the unaffected terms).
        '''
        powl = PowerLite.from_term(x)
        return self.divide_lite(powl, idx)

    @binding
    def divide_lite(self, powerlite, idx=None):
        '''divide powerlite from terms in self. (all terms if idx=None)
        i.e. subtract powerlite.exp from matching base (via 'is') in each of the terms.
        NOTE: IN-PLACE OPERATION. i.e. the PowerLites inside self will be affected.
        idx: None or iterable
            None --> return self / powerlite
            iterable --> divide terms=[self[i] for i in idx] by powerlite.
                    return (those terms / powerlite), (the unaffected terms).
        '''
        base0, exp0 = powerlite
        if idx is None:
            to_divide = self
        else:
            to_divide, to_remain = self.split(idx)
        for i, prodl in to_divide.items():
            for j, powl in prodl.items():
                if powl is powerlite:
                    prodl.pop(j)
                    break
                if powl.base is base0:
                    powl.sub_power(exp0)
                    break
            else:  # didn't find a matching base.
                prodl.append_lite(PowerLite(base0, -exp0))
        if idx is None:
            return to_divide
        else:
            return to_divide, to_remain

    @binding
    def multiply(self, x, idx=None):
        '''multiply "math object" x by terms in self. (all terms if idx=None)
        NOTE: IN-PLACE OPERATION. i.e. the PowerLites inside self will be affected.
        idx: None or iterable
            None --> return self * powerlite
            iterable --> multiply terms=[self[i] for i in idx] by powerlite.
                    return (those terms * powerlite), (the unaffected terms).
        '''
        powl = PowerLite.from_term(x)
        return self.multiply_lite(powl, idx)

    @binding
    def multiply_lite(self, powerlite, idx=None):
        '''multiply powerlite to terms in self. (all terms if idx=None)
        i.e. add powerlite.exp to matching base (via 'is') in each of the terms.
        NOTE: IN-PLACE OPERATION. i.e. the PowerLites inside self will be affected.
        idx: None or iterable
            None --> return self * powerlite
            iterable --> multiply terms=[self[i] for i in idx] by powerlite.
                    return (those terms * powerlite), (the unaffected terms).
        '''
        base0, exp0 = powerlite
        if idx is None:
            to_multiply = self
        else:
            to_multiply, to_remain = self.split(idx)
        for i, prodl in to_multiply.items():
            for j, powl in prodl.items():
                if powl is powerlite:
                    prodl.pop(j)
                    break
                if powl.base is base0:
                    powl.add_power(exp0)
                    break
            else:  # didn't find a matching base.
                prodl.append_lite(PowerLite(base0, exp0))
        if idx is None:
            return to_multiply
        else:
            return to_multiply, to_remain


''' --------------------- Compress --------------------- '''

with binding.to(SumLite):
    @binding
    def compress(self, cbins=None):
        '''replace equivalent bases throughout self. if equals(base1, base2), replace base2 with base1.
        Many methods in this module assume comparing bases via 'is' is enough to test equality.
        After compress(), that will be fine. Before, it may produce unexpected results.

        cbins: None or ComplexityBinning object
            if entered, use this as the starting point for compression;
            compare all bases with the values in here too, instead of just the values in self.
            NOTE: cbins will be edited IN-PLACE
                (unless all bases in self are already in cbins,
                then there would be no changes to cbins).

        return whether anything was compressed.
        '''
        compressed_anything = False
        if cbins is None:
            cbins = ComplexityBinning()
        for (i, j, powl) in self.flat():
            base = powl.base
            matched, (_c, i, bin_) = cbins.bin_or_index(base, return_bin=True)
            if matched:
                match = bin_[i]
                if match is not base:
                    powl.base = bin_[i]
                    compressed_anything = True
        return compressed_anything


''' --------------------- Flatten --------------------- '''

with binding.to(PowerLite):
    @binding
    def flatten(self, skip=[]):
        '''if base is a Power, put its exp into self.exp instead, unless base.base in skip (via 'is')'''
        base = self.base
        if isinstance(base, Power):
            base_base = base.base
            if all(s is not base_base for s in skip):
                self.base = base.base
                self.exp = self.exp * base.exp

with binding.to(ProductLite):
    @binding
    def flatten_powers(self, skip=[]):
        '''flatten powers in self. IN-PLACE OPERATION; self may be altered.'''
        for powl in self.values():
            powl.flatten(skip=skip)


with binding.to(SumLite):
    @binding
    def flatten_powers(self, skip=[]):
        '''flatten powers in self. IN-PLACE OPERATION; self may be altered.'''
        for i, j, powl in self.flat():
            powl.flatten(skip=skip)


''' --------------------- Collect --------------------- '''

with binding.to(ProductLite):
    @binding
    def collect(self, only=None):
        '''combine any terms in self with the same base.
        NOTE: IN-PLACE OPERATION; self will be altered if any two terms have the same base.
        only: None or list
            if provided, only collect if base is in only (via 'is')
        return indices with affected PowerLites in final version of self.
        '''
        baseid_to_powl = dict() # {id(bpowl.base): (index of bpowl in self, bpowl)}
        j_affected = []
        for i, ipowl in tuple(self.items()):  # tuple() since we might change self during loop.
            base = ipowl.base
            if (only is not None) and (not any(base is o for o in only)):
                continue  # ignore this base, since it's not in only.
            id_ = id(base)
            try:
                j, bpowl = baseid_to_powl[id_]
            except KeyError:
                baseid_to_powl[id_] = (i, ipowl)
            else:  # already saw ipowl.base before
                bpowl.add_power(ipowl.exp)
                self.pop(i)
                j_affected.append(j)
        return j_affected

with binding.to(SumLite):
    @binding
    def products_collect(self):
        '''prodl.collect() for prodl in self.values().
        returns {i: indices from self[i] with affected PowerLites in final version of self.}
        '''
        result = dict()
        for i, prodl in self.items():
            icol = prodl.collect()
            if len(icol) > 0:
                result[i] = icol
        return result


''' --------------------- Reconstruct --------------------- '''

with binding.to(PowerLite):
    @binding
    def reconstruct(self, *, simplify_id=True, force=False):
        '''returns the original Product object if available, else power(self.base, self.power).
        simplify_id applies if original is unknown and self.power == 1.
        if force, always reconstruct even if original is available.
        '''
        if not force:
            original = self.original
            if original is not None:
                return original
        base = self.base
        try:
            base_reconstruct = base.reconstruct
        except AttributeError:
            b = self.base
        else:
            b = base_reconstruct(simplify_id=simplify_id, force=force)
        return INITIALIZERS.power(b, self.exp, simplify_id=simplify_id)

with binding.to(ProductLite):
    @binding
    def reconstruct(self, *, simplify_id=True, force=False):
        '''returns the original Product object if available, else product(factors in self).
        simplify_id applies if original is unknown and any terms are 1.
        if force, always reconstruct even if original is available.
        '''
        if not force:
            original = self.original
            if original is not None:
                return original
        factors = [powl.reconstruct(simplify_id=simplify_id, force=force) for powl in self.values()]
        return INITIALIZERS.product(*factors, simplify_id=simplify_id)

with binding.to(SumLite):
    @binding
    def reconstruct(self, *, simplify_id=True, force=False):
        '''returns the original Sum object if available, else sum(summands in self).
        simplify_id applies if original is unknown and any terms are 1.
        if force, always reconstruct even if original is available.
        '''
        if not force:
            original = self.original
            if original is not None:
                return original
        summands = [prodl.reconstruct(simplify_id=simplify_id, force=force) for prodl in self.values()]
        return INITIALIZERS.sum(*summands, simplify_id=simplify_id)
