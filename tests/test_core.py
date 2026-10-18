"""Unit tests for column_alignment_sorter_utils.core."""

import unittest

from column_alignment_sorter_utils.core import sort_lines_by_column


class TestSortLinesByColumn(unittest.TestCase):
    def test_basic_sort_second_column_ascending(self):
        lines = ["alpha 3", "beta 1", "gamma 2"]
        self.assertEqual(
            sort_lines_by_column(lines, 1),
            ["beta 1", "gamma 2", "alpha 3"],
        )

    def test_descending(self):
        lines = ["a 1", "b 3", "c 2"]
        self.assertEqual(
            sort_lines_by_column(lines, 1, descending=True),
            ["b 3", "c 2", "a 1"],
        )

    def test_stable_order_for_equal_keys(self):
        # Input order is preserved among rows with identical keys.
        lines = ["x 5", "y 5", "z 5", "w 5"]
        self.assertEqual(
            sort_lines_by_column(lines, 1),
            ["x 5", "y 5", "z 5", "w 5"],
        )

    def test_default_column_zero(self):
        # column_index=0 means sort by the first token.
        lines = ["banana 2", "apple 9", "cherry 1"]
        self.assertEqual(
            sort_lines_by_column(lines, 0),
            ["apple 9", "banana 2", "cherry 1"],
        )

    def test_lines_without_enough_columns_sort_first_ascending(self):
        # A row shorter than the requested index is "less than" a row that has it.
        lines = ["b 2", "c 1", "a"]
        self.assertEqual(
            sort_lines_by_column(lines, 1),
            ["a", "c 1", "b 2"],
        )

    def test_lines_without_enough_columns_sort_last_descending(self):
        lines = ["c 1", "a", "b 2"]
        self.assertEqual(
            sort_lines_by_column(lines, 1, descending=True),
            ["b 2", "c 1", "a"],
        )

    def test_empty_input_returns_empty(self):
        self.assertEqual(sort_lines_by_column([], 0), [])

    def test_single_line(self):
        self.assertEqual(sort_lines_by_column(["solo line here"], 1), ["solo line here"])

    def test_blank_line_is_treated_as_single_token(self):
        # A blank string has zero tokens; ``""`` should therefore come first ascending.
        lines = ["b 1", "", "a 2"]
        self.assertEqual(
            sort_lines_by_column(lines, 1),
            ["", "b 1", "a 2"],
        )

    def test_whitespace_run_collapses_to_single_space(self):
        # The implementation explicitly re-joins with single spaces; a test that did not
        # match that would be asserting on behaviour we do not have.
        lines = ["zeta     4", "alpha  2"]
        self.assertEqual(
            sort_lines_by_column(lines, 1),
            ["alpha 2", "zeta 4"],
        )

    def test_negative_column_index_raises(self):
        with self.assertRaises(ValueError):
            sort_lines_by_column(["a b"], -1)

    def test_non_int_column_index_raises(self):
        with self.assertRaises(TypeError):
            sort_lines_by_column(["a b"], 1.0)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            sort_lines_by_column(["a b"], True)  # type: ignore[arg-type]

    def test_numeric_strings_sort_lexicographically(self):
        # "10" sorts before "2" because we compare as strings, not numbers.  Lexicographic
        # order here is "1" < "10" < "2".  This is the documented behaviour and the test
        # pins it.
        lines = ["a 10", "b 2", "c 1"]
        self.assertEqual(
            sort_lines_by_column(lines, 1),
            ["c 1", "a 10", "b 2"],
        )

    def test_input_not_mutated(self):
        lines = ["b 2", "a 1"]
        original = list(lines)
        sort_lines_by_column(lines, 1)
        self.assertEqual(list(lines), original)


if __name__ == "__main__":
    unittest.main()
