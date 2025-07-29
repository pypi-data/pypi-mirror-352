from collections import OrderedDict
from itertools import chain
from operator import itemgetter

import pytest
from snakeoil import sequences
from snakeoil.sequences import split_elements, split_negations


class UnhashableComplex(complex):
    def __hash__(self):
        raise TypeError


class TestStableUnique:
    def common_check(self, func):
        # silly
        assert func(()) == []
        # hashable
        assert sorted(func([1, 1, 2, 3, 2])) == [1, 2, 3]
        # neither

    def test_stable_unique(self, func=sequences.stable_unique):
        assert list(set([1, 2, 3])) == [1, 2, 3], (
            "this test is reliant on the interpreter hasing 1,2,3 into a specific ordering- "
            "for whatever reason, ordering differs, thus this test can't verify it"
        )
        assert func([3, 2, 1]) == [3, 2, 1]

    def test_iter_stable_unique(self):
        self.test_stable_unique(lambda x: list(sequences.iter_stable_unique(x)))
        o = UnhashableComplex()
        l = [1, 2, 3, o, UnhashableComplex(), 4, 3, UnhashableComplex()]
        assert list(sequences.iter_stable_unique(l)) == [1, 2, 3, o, 4]

    def _generator(self):
        for x in range(5, -1, -1):
            yield x

    def test_unstable_unique(self):
        self.common_check(sequences.unstable_unique)
        uc = UnhashableComplex
        res = sequences.unstable_unique([uc(1, 0), uc(0, 1), uc(1, 0)])
        # sortable
        assert sorted(sequences.unstable_unique([[1, 2], [1, 3], [1, 2], [1, 3]])) == [
            [1, 2],
            [1, 3],
        ]
        assert res == [uc(1, 0), uc(0, 1)] or res == [uc(0, 1), uc(1, 0)]
        assert sorted(sequences.unstable_unique(self._generator())) == sorted(range(6))


class TestChainedLists:
    @staticmethod
    def gen_cl():
        return sequences.ChainedLists(
            list(range(3)), list(range(3, 6)), list(range(6, 100))
        )

    def test_contains(self):
        cl = self.gen_cl()
        for x in (1, 2, 4, 99):
            assert x in cl

    def test_iter(self):
        assert list(self.gen_cl()) == list(range(100))

    def test_len(self):
        assert len(self.gen_cl()) == 100

    def test_str(self):
        l = sequences.ChainedLists(list(range(3)), list(range(3, 5)))
        assert str(l) == "[ [0, 1, 2], [3, 4] ]"

    def test_getitem(self):
        cl = self.gen_cl()
        for x in (1, 2, 4, 98, -1, -99, 0):
            # "Statement seems to have no effect"
            # pylint: disable=W0104
            cl[x]
        with pytest.raises(IndexError):
            cl.__getitem__(100)
        with pytest.raises(IndexError):
            cl.__getitem__(-101)

    def test_mutable(self):
        with pytest.raises(TypeError):
            self.gen_cl().__delitem__(1)
        with pytest.raises(TypeError):
            self.gen_cl().__setitem__(1, 2)

    def test_append(self):
        cl = self.gen_cl()
        cl.append(list(range(10)))
        assert len(cl) == 110

    def test_extend(self):
        cl = self.gen_cl()
        cl.extend(list(range(10)) for i in range(5))
        assert len(cl) == 150


class Test_iflatten_instance:
    func = staticmethod(sequences.iflatten_instance)

    def test_it(self):
        o = OrderedDict((k, None) for k in range(10))
        for l, correct, skip in (
            (
                ["asdf", ["asdf", "asdf"], 1, None],
                ["asdf", "asdf", "asdf", 1, None],
                str,
            ),
            ([o, 1, "fds"], [o, 1, "fds"], (str, OrderedDict)),
            ([o, 1, "fds"], list(range(10)) + [1, "fds"], str),
            ("fds", ["fds"], str),
            ("fds", ["f", "d", "s"], int),
            ("", [""], str),
            (1, [1], int),
        ):
            iterator = self.func(l, skip)
            assert list(iterator) == correct
            assert list(iterator) == []

        # There is a small difference between the cpython and native
        # version: the cpython one raises immediately, for native we
        # have to iterate.
        def fail():
            return list(self.func(None))

        with pytest.raises(TypeError):
            fail()

        # Yes, no sane code does this, but even insane code shouldn't
        # kill the cpython version.
        iters = []
        iterator = self.func(iters)
        iters.append(iterator)
        with pytest.raises(ValueError):
            next(iterator)

        # Regression test: this was triggered through demandload.
        # **{} is there to explicitly force a dict.
        assert self.func((), **{})


class Test_iflatten_func:
    func = staticmethod(sequences.iflatten_func)

    def test_it(self):
        o = OrderedDict((k, None) for k in range(10))
        for l, correct, skip in (
            (
                ["asdf", ["asdf", "asdf"], 1, None],
                ["asdf", "asdf", "asdf", 1, None],
                str,
            ),
            ([o, 1, "fds"], [o, 1, "fds"], (str, OrderedDict)),
            ([o, 1, "fds"], list(range(10)) + [1, "fds"], str),
            ("fds", ["fds"], str),
            (1, [1], int),
        ):
            iterator = self.func(l, lambda x: isinstance(x, skip))
            assert list(iterator) == correct
            assert list(iterator) == []

        # There is a small difference between the cpython and native
        # version: the cpython one raises immediately, for native we
        # have to iterate.
        def fail():
            return list(self.func(None, lambda x: False))

        with pytest.raises(TypeError):
            fail()

        # Yes, no sane code does this, but even insane code shouldn't
        # kill the cpython version.
        iters = []
        iterator = self.func(iters, lambda x: False)
        iters.append(iterator)
        with pytest.raises(ValueError):
            next(iterator)

        # Regression test: this was triggered through demandload.
        # **{} is there to explicitly force a dict to the underlay cpy
        assert self.func((), lambda x: True, **{})


class Test_predicate_split:
    kls = staticmethod(sequences.predicate_split)

    def test_simple(self):
        false_l, true_l = self.kls(lambda x: x % 2 == 0, range(100))
        assert false_l == list(range(1, 100, 2))
        assert true_l == list(range(0, 100, 2))

    def test_key(self):
        false_l, true_l = self.kls(
            lambda x: x % 2 == 0, ([0, x] for x in range(100)), key=itemgetter(1)
        )
        assert false_l == [[0, x] for x in range(1, 100, 2)]
        assert true_l == [[0, x] for x in range(0, 100, 2)]


class TestSplitNegations:
    def test_empty(self):
        # empty input
        seq = ""
        assert split_negations(seq) == ((), ())

    def test_bad_value(self):
        # no-value negation should raise a ValueError
        bad_values = (
            "-",
            "a b c - d f e",
        )

        for s in bad_values:
            with pytest.raises(ValueError):
                split_negations(s.split())

    def test_negs(self):
        # all negs
        seq = ("-" + str(x) for x in range(100))
        assert split_negations(seq) == (tuple(map(str, range(100))), ())

    def test_pos(self):
        # all pos
        seq = (str(x) for x in range(100))
        assert split_negations(seq) == ((), tuple(map(str, range(100))))

    def test_neg_pos(self):
        # both
        seq = (("-" + str(x), str(x)) for x in range(100))
        seq = chain.from_iterable(seq)
        assert split_negations(seq) == (
            tuple(map(str, range(100))),
            tuple(map(str, range(100))),
        )

    def test_converter(self):
        # converter method
        seq = (("-" + str(x), str(x)) for x in range(100))
        seq = chain.from_iterable(seq)
        assert split_negations(seq, int) == (tuple(range(100)), tuple(range(100)))


class TestSplitElements:
    def test_empty(self):
        # empty input
        seq = ""
        assert split_elements(seq) == ((), (), ())

    def test_bad_value(self):
        # no-value neg/pos should raise ValueErrors
        bad_values = (
            "-",
            "+",
            "a b c - d f e",
            "a b c + d f e",
        )

        for s in bad_values:
            with pytest.raises(ValueError):
                split_elements(s.split())

    def test_negs(self):
        # all negs
        seq = ("-" + str(x) for x in range(100))
        assert split_elements(seq) == (tuple(map(str, range(100))), (), ())

    def test_neutral(self):
        # all neutral
        seq = (str(x) for x in range(100))
        assert split_elements(seq) == ((), tuple(map(str, range(100))), ())

    def test_pos(self):
        # all pos
        seq = ("+" + str(x) for x in range(100))
        assert split_elements(seq) == ((), (), tuple(map(str, range(100))))

    def test_neg_pos(self):
        # both negative and positive values
        seq = (("-" + str(x), "+" + str(x)) for x in range(100))
        seq = chain.from_iterable(seq)
        assert split_elements(seq) == (
            tuple(map(str, range(100))),
            (),
            tuple(map(str, range(100))),
        )

    def test_neg_neu_pos(self):
        # all three value types
        seq = (("-" + str(x), str(x), "+" + str(x)) for x in range(100))
        seq = chain.from_iterable(seq)
        assert split_elements(seq) == (
            tuple(map(str, range(100))),
            tuple(map(str, range(100))),
            tuple(map(str, range(100))),
        )

    def test_converter(self):
        # converter method
        seq = (("-" + str(x), str(x), "+" + str(x)) for x in range(100))
        seq = chain.from_iterable(seq)
        assert split_elements(seq, int) == (
            tuple(range(100)),
            tuple(range(100)),
            tuple(range(100)),
        )
