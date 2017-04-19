# -*- coding: utf-8 -*-

import unittest
from game24 import SuffixFormula, FormulaGenerator, find


class TestSuffixFormula(unittest.TestCase):
    def test_push_ok(self):
        sf = SuffixFormula()
        res = sf.push(1)
        self.assertEqual(res, True)
        res = sf.push(2)
        self.assertEqual(res, True)

        res = sf.push('+')
        self.assertEqual(res, True)
        self.assertEqual(sf.invalid, True)
        self.assertEqual(sf.value(), 3)

    def test_push_error_1(self):
        sf = SuffixFormula()
        res = sf.push('+')
        self.assertEqual(res, False)
        self.assertEqual(sf.invalid, False)

        res = sf.push(1)
        self.assertEqual(res, False)

    def test_push_error_2(self):
        sf = SuffixFormula()
        res = sf.push(1)
        self.assertEqual(res, True)
        res = sf.push(0)
        self.assertEqual(res, True)

        res = sf.push('/')
        self.assertEqual(res, False)
        self.assertEqual(sf.invalid, False)

    def test_find_sub_sequence_index_1(self):
        sequence = [1, 2, 3]

        with self.assertRaises(ValueError):
            SuffixFormula._find_sub_sequence_index(sequence, 2)

    def test_find_sub_sequence_index_2(self):
        sequence = [1, '+']

        with self.assertRaises(ValueError):
            SuffixFormula._find_sub_sequence_index(sequence, 1)

    def test_find_sub_sequence_index_3(self):
        sequence = [1, 2, '+']
        index = SuffixFormula._find_sub_sequence_index(sequence, 2)
        self.assertEqual(index, 0)

    def test_find_sub_sequence_index_4(self):
        sequence = [1, 2, '+', 3, '*']
        index = SuffixFormula._find_sub_sequence_index(sequence, 4)
        self.assertEqual(index, 0)

    def test_normalize_remove_brackets_1(self):
        # 6 * (5 + (5 - 6)) => 6 5 5 6 - + *
        # 6 * (5 + 5 - 6)   => 6 5 5 + 6 - *
        sequence = [6, 5, 5, 6, '-', '+', '*']
        expected = [6, 5, 5, '+', 6, '-', '*']

        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        new_seq = sf._normalize_remove_brackets(sequence, '+')
        self.assertEqual(new_seq, expected)

    def test_normalize_remove_brackets_2(self):
        # 6 + (5 + 5 * 6) => 6 5 5 6 * + +
        # 6 + 5 + 5 * 6   => 6 5 + 5 6 * +
        sequence = [6, 5, 5, 6, '*', '+', '+']
        expected = [6, 5, '+', 5, 6, '*', '+']

        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        new_seq = sf._normalize_remove_brackets(sequence, '+')
        self.assertEqual(new_seq, expected)

    def test_normalize_exchange_1(self):
        sequence = [2, 1, '+']
        expected = [1, 2, '+']
        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        new_seq = sf._normalize_exchange(sequence)
        self.assertEqual(new_seq, expected)

    def test_normalize_exchange_2(self):
        # (1 + 2) * (3 + 4) => 1 2 + 3 4 + *
        sequence = [1, 2, '+', 3, 4, '+', '*']
        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        new_seq = sf._normalize_exchange(sequence)
        self.assertEqual(new_seq, sequence)

    def test_normalize_exchange_3(self):
        # (4 + 3) * (2 + 1) => 4 3 + 2 1 + *
        # (1 + 2) * (3 + 4) => 1 2 + 3 4 + *
        sequence = [4, 3, '+', 2, 1, '+', '*']
        expected = [1, 2, '+', 3, 4, '+', '*']
        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        new_seq = sf._normalize_exchange(sequence)
        self.assertEqual(new_seq, expected)

    def test_normalize_exchange_special_1(self):
        sequence = [1, 2, '-', 3, '-']
        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        new_seq = sf._normalize_exchange_special(sequence, '-')
        self.assertEqual(new_seq, sequence)

    def test_normalize_exchange_special_2(self):
        sequence = [3, 2, '-', 1, '-']
        expected = [3, 1, '-', 2, '-']
        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        new_seq = sf._normalize_exchange_special(sequence, '-')
        self.assertEqual(new_seq, expected)

    def test_normalize_same_op_1(self):
        sequence = [1, 2, 3, 4, '*', '*', '*']
        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        new_seq = sf._normalize_same_op(sequence, '*')
        self.assertEqual(new_seq, sequence)

    def test_normalize_same_op_2(self):
        # 4 * 2 * 1 * 3
        # 1 * (2 * (3 * 4))
        sequence = [4, 2, '*', 1, '*', 3, '*']
        expected = [1, 2, 3, 4, '*', '*', '*']
        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        new_seq = sf._normalize_same_op(sequence, '*')
        self.assertEqual(new_seq, expected)

    def test_to_infix_1(self):
        sequence = [1, 2, 3, 4, '*', '*', '*']
        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        self.assertEqual(sf.to_infix(), "1 * (2 * (3 * 4))")

    def test_to_infix_2(self):
        sequence = [1, 2, '+', 3, '*', 4, '+', 5, '/']
        sf = SuffixFormula()
        for s in sequence:
            sf.push(s)

        self.assertEqual(sf.to_infix(), "(4 + (3 * (1 + 2))) / 5")


class TestFormulaGenerator(unittest.TestCase):
    def test_gen_1(self):
        numbers = [1, 2]
        fg = FormulaGenerator(*numbers)
        for seq in fg:
            self.assertEqual(len(seq), 3)
            self.assertIn(seq[2], ['+', '-', '*', '/'])


class TestFind(unittest.TestCase):
    def test_find_1(self):
        result = find(3, 1, 2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], '1 + 2')

    def test_find_2(self):
        result = find(10, 1, 2)
        self.assertEqual(len(result), 0)
