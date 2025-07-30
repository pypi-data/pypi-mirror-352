"""
File Purpose: AbstractProduct
Implements rules common to all products (e.g. scalar product, dot product, cross product):
    - the distributive property: x * (y + z) --> x * y + x * z, for '*' a product operation
    - product == 0, if any of the factors in any product are 0
    - counting number of minus signs which appear in factors
        - (this one is mostly just an implementation detail.)

The distributive property relies on isinstance(obj, Sum),
    which is why AbstractProduct is defined in after Sum in basics, rather than in abstracts.
"""
import builtins
from ..basics_tools import (
    get_summands, count_minus_signs_in_factors,
)
from ...abstracts import (
    IterableSymbolicObject, AbstractOperation,
    SimplifiableObject, SubbableObject,
    _equals0,
    simplify_op, expand_op,
)
from ...tools import (
    alias,
    caching_attr_simple_if,
)
from ...defaults import DEFAULTS


class AbstractProduct(IterableSymbolicObject, SimplifiableObject,
                      AbstractOperation, SubbableObject):
    '''a Product object, in the sense that the distributive property works.
    Also, if any of the terms are 0, self == 0 as well.
    Also, provides methods for counting minus signs, e.g. to determine if self "seems negative".
    '''
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def _equals0(self):
        '''returns whether self == 0.'''
        return any(_equals0(t) for t in self)

    # # # COUNTING MINUS SIGNS # # #
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def count_minus_signs_in_factors(self):
        '''counts number of factors in self with minus signs.'''
        return builtins.sum(count_minus_signs_in_factors(t) for t in self)

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def has_minus_sign(self):
        '''returns whether self has a leading minus sign when considered as a string.'''
        return self.count_minus_signs_in_factors() > 0

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def seems_negative(self):
        '''returns whether self seems negative - i.e. has an odd number of minus signs.'''
        return (self.count_minus_signs_in_factors() % 2) == 1

    def seems_positive(self):
        return not self.seems_negative()


@simplify_op(AbstractProduct, alias='_simplify_id')
def _abstract_product_simplify_id(self, **kw__None):
    '''converts 0 * x --> 0 at top layer of self.
    returns 0 if _equals0(self), else returns self.
    '''
    return 0 if self._equals0() else self

@expand_op(AbstractProduct, alias='_distribute')
def _abstract_product_distribute(self, distribute_sum_if=lambda x: True, **kw__None):
    '''distributes at top layer of self. x * (y + z) --> x * y + x * z.
    distribute_sum_if: callable of one input, default f(x) --> True.
        allows for more fine-tuned control over which sums to distribute.
        for each factor in self,
            if get_summands(factor) returns more than 1 value (e.g. because factor is a Sum),
            only distribute those summands if distribute_if(factor).
        This function will only receive input values for which len(get_summand(value))>1.
    '''
    # setup
    iter_self = iter(self)
    self_factor_0 = next(iter_self)
    def _get_summands_to_distribute(factor):
        summands = get_summands(factor)
        if len(summands) > 1:
            if not distribute_sum_if(factor):
                return [factor]
        return summands
    factor_0_summands = _get_summands_to_distribute(self_factor_0)
    distributed_any = (len(factor_0_summands) > 1)
    # stores list of summands in result, with each summand represented as a list of factors.
    # (we need to start with the first factor in self so we have something to distribute to.
    #  we could've started with Product.IDENTITY instead, but that's less efficient,
    #  and we don't know, maybe self.IDENTITY is not available for all AbstractProducts.)
    result_summands_as_factors = [[summand] for summand in factor_0_summands]
    # loop through remaining factors, distributing (when appropriate)
    for self_factor in iter_self:
        factor_summands = _get_summands_to_distribute(self_factor)
        if len(factor_summands) > 1:
            # factor is a sum. distribute each summand to result.
            # e.g. result [[x],[5,y],[u]] * summands [8,z] --> [[x,8],[5,y,8],[u,8],[x,z],[5,y,z],[u,z]].
            distributed_any = True
            result_summands_as_factors = [rsummand_as_factors + [fsummand]
                    for fsummand in factor_summands
                    for rsummand_as_factors in result_summands_as_factors]
        else:
            # factor is not a sum. for efficiency we append it to existing lists in result.
            # (a less-efficient implementation would just re-use the exact same code as above,
            #  but that would always iterating through each list in result to make new lists,
            #  rather than just appending to existing list for each term in result.)
            for rsummand_as_factors in result_summands_as_factors:
                rsummand_as_factors.append(factor_summands[0])
                # the explicit [0] indexing means an error will be raised if len(factor_summands)==0.
                # That's good; we expect len(factor_summands) >= 1.
    if not distributed_any:
        return self  # return self, exactly, to help indicate nothing was changed.
    # make new Sum using all the distributed terms.
    result_summands = (self._new(*factors) for factors in result_summands_as_factors)
    return self.sum(*result_summands)