"""
File Purpose: greedy sum collect algorithm
"""
import builtins   # for unambiguous sum

from .sum import Sum

from ._lites import PowerLite, ProductLite, SumLite
from .basics_tools import seems_negative, get_factors, get_summands

from ..abstracts import (
    simplify_op, simplify_op_skip_for,
    complexity,
    contains_deep,
)
from ..tools import (
    equals, max_number,
    _list_without_i,
)

from ..defaults import ONE, MINUS_ONE


''' --------------------- sum collect greedy --------------------- '''

#simplify_op_skip_for(Sum, '_sum_collect_greedy')

@simplify_op(Sum, alias='_collect', order=10)  # large order <--> try most other simplify ops before this one.
def _sum_collect_greedy(self, collect_polys=[], collect_poly_format=False, **kw__None):
    '''greedy sum collect.
    The algorithm is roughly:
        - "compress" object (so that factors can be compared via 'is')
        - start checking factors which appeared multiple times during compression
            - check factors in order from highest complexity to lowest complexity
            - if factor is shared by ANY other summand, collect.
                - then, look inside collected summands for more collections
                - then, look inside uncollected summands for more collections

    collect_polys: list, default empty list.
        bases in this list only match for collection if the exponents match too.
        when determining complexities, add a big number if term.contains_deep(base)
        ("big number" = max of actual complexities)
    collect_poly_format: bool, default False
        if True, only collect if collect_polys are not present in terms being collected.

    [EFF] first attempt, doesn't optimize "base and exponents matching"
    [TODO] first attempt, don't match new sums with existing sums.. maybe..
    '''
    DONT_COLLECT = [MINUS_ONE]  # list of things to not collect. (maybe let user input others via kwarg?)

    suml = SumLite.from_term(self, polys=collect_polys)
    suml.flatten_powers(skip=collect_polys)
    suml.products_collect()

    # initial candidates for collecting
    # # bases_and_indices = {id(base): (base, indices)}, with indices like {i0: j0, ...}
    kw__get_bi = dict(polys=collect_polys) if collect_poly_format else dict()
    bases_and_indices = suml.bases_and_i_to_j(**kw__get_bi)
    candidates = {id_: bi for id_, bi in bases_and_indices.items()   # bi looks like (base, indices)
                        if len(bi[1]) > 1        # len(indices) > 1, i.e. base appears in 2+ places
                        and not any(equals(bi[0], dc) for dc in DONT_COLLECT)  # skip things in DONT_COLLECT.
                 }
    complexities = {id_: complexity(base) for id_, (base, indices) in candidates.items()}

    if len(collect_polys) > 0:
        max_complexity = max(complexities.values()) if len(complexities) > 0 else None
        for id_, (base, indices) in candidates.items():
            if any(contains_deep(base, poly) for poly in collect_polys):
                complexities[id_] = complexities[id_] + max_complexity

    while len(candidates) > 0:
        # sort candidates by complexity (most complex is candidates_order[0])
        candidates_order = sorted(candidates.keys(), key=lambda k: complexities[k], reverse=True)

        # >> collecting happens here <<
        # collect the most complex candidate from all summands which have it;
        # also collect any other candidates shared amongst those summands.
        # also deletes candidates_order[0]
        suml = _collect_lite(suml, candidates, candidates_order, complexities)

        # >> next, decide new candidates <<
        # There's probably a smart way to reuse the indices info, but it would be tricky.
        # Less likely to make coding errors if we just recalculate the bases_and_indices.

        # get new candidates, utilizing that these must be a subset of the old candidates.
        # [TODO][EFF] definitely should be possibly to re-use information,
        #   if we improve the bookkeeping somehow. But it's tricky; only worthwhile if slow.
        bases_and_indices = suml.bases_and_i_to_j()
        candidates = dict()
        for id_ in candidates_order:
            # put id_ into candidates1 if it is in bases_and_indices1 with len(indices)>1,
            # otherwise, we won't consider that candidate anymore.
            # It's possible for id_ to appear in fewer places now than before,
            #    if it occured in some but not all summands in irreducible0.
            try:
                bi = bases_and_indices[id_]
            except KeyError:
                pass  # that's fine, we will just skip this base.
            else:
                if len(bi[1]) > 1:
                    candidates[id_] = bi

    return suml.reconstruct()  # if no candidates were collected, this will return self, exactly.


def _collect_lite(suml, candidates, candidates_order, complexities):
    '''helper method for _sum_collect_greedy. Does the following:
    - collect most complex candidate from all summands which have it. (-->factor0)
        - remove that candidate from candidates_order
    - collect all other shared factors from the affected summands. (-->fcollected)
        - don't remove those factors from candidates; other summands might have them too.
    - combine the result into one SumLite and return it. (-->suml_result)
    '''
    # collect the most complex candidate from all summands which have it.
    id0 = candidates_order[0]
    base0, indices0 = candidates[id0]
    factor0, divided, unaffected = suml.divide_min_power_from(indices0)
    # remove factor0 from candidates
    del candidates_order[0]

    # collect all other shared factors from the affected summands
    fcollected = [factor0]
    for id_ in candidates_order:
        baseC, indicesC = candidates[id_]
        if set(divided.keys()).issubset(indicesC.keys()):  # baseC appears in ALL terms in divided. So, collect baseC too.
            indices_collect = {i: indicesC[i] for i in divided}
            factorC, divided, _emptyC = divided.divide_min_power_from(indices_collect)
            assert len(_emptyC) == 0
            fcollected.append(factorC)
            
    # now, divided is an irreducible sum (SumLite). irreducible i.e. no shared bases.
    irreducible = divided.reconstruct()
    if all(term is ONE for term in irreducible):
        # replace 1 + 1 with 2. Avoids loop with associative_flatten, when evaluate_numbers=False
        assert isinstance(irreducible, Sum)    # < pretty sure this is True, but asserting it just in case.
        irreducible = len(irreducible)
    irr_lite = PowerLite.from_term(irreducible)
    prodlC = ProductLite.from_lites((*fcollected, irr_lite))
    suml_result = unaffected
    suml_result.append_lite(prodlC)
    return suml_result


''' --------------------- sum collect fractionize --------------------- '''

@simplify_op(Sum, alias='_collect', order=12)
def _sum_collect_fractionize(self, **kw__None):
    '''sum collect which makes result look like a fraction.
    E.g. X^-1 + 5 --> (X + 5)/X
    '''
    # setup
    suml = SumLite.from_term(self)
    suml.flatten_powers()
    suml.products_collect()  # combine any shared bases within the same product.

    # denominator factors
    bases_and_indices = suml.bases_and_i_to_j()   # {id(base): (base, indices)} indices like {i0: j0, i1: j1, ...}
                                                  # iN != iM (for N!=M) is guaranteed because of products_collect().

    min_powers = {id_: suml.min_power_from(indices.items(), return_index=True) # (min_power, (i, j) of powl with min power)
                  for id_, (base, indices) in bases_and_indices.items()}
    denom_indices = {id_: index for id_, (power, index) in min_powers.items() if seems_negative(power)}

    if len(denom_indices) == 0:
        return suml.reconstruct()  # might return self if self was unaffected.

    prodl = ProductLite.from_lites(suml[i][j] for i, j in denom_indices.values())
    for powl in prodl.values():
        suml.divide_lite(powl)

    sum_col = suml.reconstruct()
    try:
        sum_col = sum_col._flatten()
    except AttributeError:
        pass  # that's fine.

    return prodl.reconstruct() * sum_col


''' --------------------- sum product collect --------------------- '''

@simplify_op(Sum, alias='_collect', order=8)   # order -- just before sum_collect_greedy & sum_collect_fractionize
def _sum_product_collect(self, **kw):
    '''product collect for all products in self; also power collect the product factors'''
    suml = SumLite.from_term(self)
    suml.products_collect()
    return suml.reconstruct()


''' --------------------- sum collect sums --------------------- '''

@simplify_op(Sum, alias='_collect', order=15)  # order -- after the other sum collects.
def _sum_collect_sums(self, collect_polys=[], collect_poly_format=False, **kw):
    '''collect sums within sums. E.g. (3 + X + 5 + Y (X + 5)) --> (3 + (X + 5) (1 + Y)).
    The full pattern is:
        A + Y (X + Z) + X + Z --> A + (Y + 1) (X + Z)
    where A, X, Y, Z can each be any expression.

    This involves looking for terms in self with a Sum factor,
        and checking if all summands inside that factor also appear separately inside self.

    Skip this simplification if collect_poly_format AND any relevant terms are in collect_polys.
        In the pattern above, "revelent terms" means X, Y, or Z.

    This doesn't look for any other matching factors;
        those should be handled by other sum collects.
        As a consequence, the newly-created sum ((1 + Y) in the example above)
            will ALWAYS have a summand equal to 1.
        Otherwise, a different sum collect will be responsible.
            E.g. (3 + 2 X + 10 + Y (X + 5)) won't be simplified here,
            but other sum collects should simplify it to:
                (3 + 2 (X + 5) + Y (X + 5)), and then to (3 + (2 + Y)(X + 5))
    This also doesn't perform the collection multiple times in one call;
        as soon as any collection is performed the result is returned immediately.

    [TODO] handle Y (X + Z) - X - Z. maybe with a different method.
        currently that will "usually" not be handled (unless rearranged by canonical_signs)
    '''
    L = len(self)
    if L < 3:  # nothing to do if not at least 3 summands.
        return self  # return self, exactly, to help indicate nothing was changed.

    # this implementation makes a "reasonable" assumption about complexity:
    #   sum of complexities for summands < complexity of ((sum of summands) * other factors).
    # e.g. assume (complexity(X) + complexity(Z)) < complexity(Y * (X + Z)) for all X, Y, Z.
    # this enables us to limit the number of summands we need to check!
    #   we sort by complexity, then we can stop as soon as there are fewer than 2 less-complex summands.
    #   additionally, we only need to check the less-complex summands at any given time.
    # [TODO] refactor to call helper methods; this function feels too long.

    cinfos = self.complexity_infosort(reverse=True)  # (i, term, complexity(term)); list(self)[i] == term.
    j_next_lowest_c = 0  # maintain complexity at j_next_lowest_c < complexity at j
    for j, (iorig, term, c) in enumerate(cinfos):
        # check if term is a product with Sum factor matching any combination of summands in self;
        #  (using complexity assumption above to reduce number of combinations we need to test)
        # if any match is found, collect & return result.
        # << first check that term is a product; we can skip if it isn't.
        factors = get_factors(term)
        if len(factors) == 1:
            continue  # term is not a product, so it has no Sum factors.
        # << term is a product; might have a least 1 sum factor; check if there's enough terms left to matter.
        if j >= j_next_lowest_c:
            try:
                j_next_lowest_c = next(k for k in range(j+1, L) if cinfos[k][2] < c)
            except StopIteration:  # no lower complexity summands remaining.
                break
            if j_next_lowest_c > (L - 2):  # fewer than 2 less-complex summands remaining.
                break
        # << check collect_polys stuff
        if collect_poly_format and any(contains_deep(term, _poly) for _poly in collect_polys):
            continue  # don't try collecting this term since it has a poly in it.
        # << term is a product and there are at least 2 less-complex summands remaining
        for fidx, factor in enumerate(factors):
            # check if factor is a Sum factor matching any combination of summands in self;
            #  (using complexity comparisons to reduce number of combinations we need to test)
            fsummands = get_summands(factor)
            L_fsummands = len(fsummands)
            if L_fsummands == 1:
                continue  # factor is not a Sum.
            if L_fsummands > (L - j_next_lowest_c):
                continue  # fewer unchecked summands remaining than amount appearing in this factor.
            # << factor is a Sum; start trying to match complexities
            cfsummands = [complexity(fsummand) for fsummand in fsummands]
            # check for complexity match for max complexity before trying anything else.
            if max(cfsummands) > cinfos[j_next_lowest_c][2]:
                # the most complex remaining candidate summand from self
                #   is less complex than the most complex summand in factor.
                continue  # that means there's no way all the summands from factor appear in self.
            # max complexity quickcheck seems okay, devote computational time to checking for match.
            # << from this point on, either find a match and return result, or continue to next factor.
            fcinfos = [(_i, _y, _cy) for _i, (_y, _cy) in enumerate(zip(fsummands, cfsummands))]
            fcinfos = sorted(fcinfos, key=lambda _cfinf: _cfinf[2], reverse=True)
            matching = []
            found_match = False
            ktest = {k: cinfos[k] for k in range(j_next_lowest_c, L)}  # all the possible summands to match.
            k_min_bound_c = j_next_lowest_c
            for fcinfo in fcinfos:  # fill matching with pairs (cinfo, fcinfo) for full match, if possible.
                fi, fy, fc = fcinfo
                found_match = False
                k = k_min_bound_c  # k must be at least this large due to complexity matching.
                while k < L:
                    try:
                        (si, sy, sc) = ktest[k]
                    except KeyError:  # already matched this summand from self to a different summand from factor.
                        k = k + 1
                        continue
                    if sc > fc:  # sc too complex; we can increase k_min_bound_c since fcinfos are in complexity order.
                        k = k + 1
                        k_min_bound_c = k
                        continue
                    elif sc < fc:
                        break  # no match found for this summand
                    # else, complexity matches! check if terms match too.
                    if equals(sy, fy):
                        cinfo = ktest.pop(k)
                        matching.append((cinfo, fcinfo))
                        found_match = True
                        break  # we matched fy, hurray!
                    # if terms don't match, that's perfectly fine;
                    # increment k and try the next term.
                    k = k + 1
                if not found_match:
                    break
            if not found_match:  # found at least one summand from this factor which is not in self.
                continue   # so, try the next factor instead.
            # << found a match! All summands from this factor match summands in self,
            # and all the matches are stored in matching as (cinfo, fcinfo).
            # now we just need to do the proper bookkeeping and return the result.
            # the pattern is A + Y (X + Z) + X + Z --> A + (Y + 1) (X + Z)
            #   X + Z <--> factor
            #   Y <--> other_factors
            #   A <--> keep_summands
            other_factors = _list_without_i(factors, fidx)
            matched_summands_i = [cinfo[0] for cinfo, fcinfo in matching]
            keep_summands_i = set(range(L)) - set(matched_summands_i) - {iorig}
            self_list = list(self)
            keep_summands = [self_list[i] for i in keep_summands_i]
            collected = self.product(factor, self.sum(ONE, self.product(*other_factors)))
            return self.sum(collected, *keep_summands)
    return self  # return self, exactly, to help indicate nothing was changed.
  