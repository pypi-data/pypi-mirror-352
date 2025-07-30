r"""
File Purpose: string representations of vector objects.
"""

from .binary_vector_products import BinaryVectorProduct
from .dot_product import DotProduct, DotProductBase
from .cross_product import CrossProduct, CrossProductBase
from .vectors_tools import (
    is_vector,
)
from ..basics._string_rep import (
    StringEncInfo, str_protector, str_info_pia,        
)
from ..basics import (
    Symbol, Sum, Product, Power,
)
from ..tools import (
    Binding,
)

binding = Binding(locals())


''' --------------------- str for BinaryVectorProduct --------------------- '''

# # # HELPER FUNCTIONS # # #
@str_protector
def _str_protect_bvp_first(x):
    '''returns whether x needs protecting due to being the first factor in a BinaryVectorProduct.
    returns x._str_protect_bvp_first(), if available,
    else returns x._str_protect_bvp(), if available.
    otherwise, returns True.
    '''
    try:
        return x._str_protect_bvp_first()
    except AttributeError:
        try:
            return x._str_protect_bvp()
        except AttributeError:
            return True

@str_protector
def _str_protect_bvp_second(x):
    '''returns whether x needs protecting due to being the second factor in a BinaryVectorProduct.
    returns x._str_protect_bvp_second(), if available,
    else returns x._str_protect_bvp(), if available.
    otherwise, returns True.
    '''
    try:
        return x._str_protect_bvp_second()
    except AttributeError:
        try:
            return x._str_protect_bvp()
        except AttributeError:
            return True

with binding.to(Symbol):
    @binding
    def _str_protect_bvp(self):
        '''returns False, because str doesn't need protecting as either factor in a binary vector product.'''
        return False

with binding.to(Sum):
    @binding
    def _str_protect_bvp(self):
        '''returns True, because str needs protecting if it is either factor in a binary vector product.'''
        return True

with binding.to(Product):
    @binding
    def _str_protect_bvp_first(self):
        '''returns True, because str needs protecting if it is the first factor in a binary vector product.'''
        return True

    @binding
    def _str_protect_bvp_second(self):
        '''returns True, because str needs protecting if it is the second factor in a binary vector product.'''
        return True

# # # BINDING STR TO BINARY VECTOR PRODUCT # # #
with binding.to(BinaryVectorProduct):
    @binding
    def _str_protect_bvp(self):
        '''returns True, because str needs protecting if it is either factor in a binary vector product.'''
        return True

    @binding
    def _str_info(self, enc=None, **kw):
        '''string for self, and info about enclosure in parentheses or brackets.

        enc: None or '()' or '[]'.
            if None, ignore. otherwise, force outermost enc in self to this value.

        [TODO] encapsulate this code into BinarySymbolicObject,
            instead of copy-pasting much of it from Power._str_info.
        '''
        v1_protect = _str_protect_bvp_first(self[0])
        v2_protect = _str_protect_bvp_second(self[1])
        v1_sinfo = str_info_pia(self[0], v1_protect, enc=enc, **kw)
        v2_sinfo = str_info_pia(self[1], v2_protect, enc=enc, **kw)
        v1_str = str(v1_sinfo)
        v2_str = str(v2_sinfo)
        self_str = f'{v1_str} {self._PRODUCT_STRING} {v2_str}'
        self_enc = v1_sinfo.enc
        return StringEncInfo(self_str, self_enc, protected=v1_protect)

    # note: we don't bind this method to BinaryVectorProduct, but call it in the _PRODUCT_STRING property below.
    def _raise_product_string_not_implemented(obj):
        '''raises NotImplementedError about obj._PRODUCT_STRING,
        to indicate obj._PRODUCT_STRING must be implemented to convert obj to string.
        '''
        errmsg = (f'{type(obj).__name__}._PRODUCT_STRING. This is required to convert to string.'
                  'It should be set to the string that goes between factors in BinaryVectorProduct.'
                  r'E.g. _PRODUCT_STRING = "\dot" for dot products.')
        raise NotImplementedError(errmsg)

    BinaryVectorProduct._PRODUCT_STRING = property(
            lambda self: _raise_product_string_not_implemented(self),
            doc= r'''The string that goes between factors, e.g. '\dot' for dot products.''')


''' --------------------- str for DotProduct --------------------- '''

DotProductBase._PRODUCT_STRING = r'\cdot'


''' --------------------- str for CrossProduct --------------------- '''

CrossProductBase._PRODUCT_STRING = r'\times'


''' --------------------- protect BinaryVectorProduct from Product, Power --------------------- '''

with binding.to(BinaryVectorProduct):
    @binding
    def _str_protect_product_factor(self, pre_factors=[], post_factors=[], **kw):
        '''returns whether self needs protecting due to being a factor in Product.
        In particular, returns whether there is a vector in pre_factors, OR there are ANY post_factors.
        Though this particular protection is not required, it does make things easier to read.
        '''
        return (len(post_factors) > 0) or any(is_vector(factor) for factor in pre_factors)

    @binding
    def _str_protect_power_base(self, **kw__None):
        '''returns True, because str needs protecting if it appears in base of Power.'''
        return True
