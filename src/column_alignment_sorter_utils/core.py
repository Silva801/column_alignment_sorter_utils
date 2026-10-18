"""Core sorting logic for column-aligned text.

Design decisions
-----------------
*  **Whitespace split.**  Columns are delimited by runs of whitespace.  This is what every
   alignment tool I have actually seen produces, and it makes the output easy to read in a
   terminal.  A tab is treated as a delimiter just like a space.  The alternative — fixed
   character offsets — requires the caller to measure widths, which collides with tabs and
   multi-code-point graphemes.  Picking whitespace-delimited means we cannot perfectly
   handle inter-column runs of spaces, but we don't have to; we just need to reconstruct.
*  **Reconstruction.**  When the original separator between column k and column k+1 is a
   run of at least one whitespace character, we preserve exactly one space (' ').  We do
   not attempt to preserve the original column width, because sorting by one column breaks
   inter-row alignment for every other column anyway.  The faithful behaviour is to return
   the same tokens in a new order, joined by single spaces, so the caller can re-align if
   desired.
*  **Key selection.**  A line that has fewer columns than the requested index sorts first
   (ascending) / last (descending).  This matches the intuition that missing data is "less
   than" present data and keeps the sort stable for equal-but-missing rows.
*  **Stability.**  `sorted` is stable in Python, so rows with equal keys keep their input
   order.  We never fall back to secondary keys because that would impose an ordering the
   caller did not ask for.
*  **No coercion.**  A key that looks numeric is compared as a string.  Numeric parsing is
   a separate concern; doing it implicitly surprises the caller when `"10"` sorts after
   `"2"`.
"""

from __future__ import annotations

from typing import List, Sequence

__all__ = ["sort_lines_by_column"]


def _split_preserving(line: str):
    """Split *line* on whitespace, returning both the tokens and the raw separator strings.

    Returns a tuple ``(tokens, seps)`` where ``tokens`` has one more entry than ``seps``.
    ``seps[k]`` is the whitespace run between ``tokens[k]`` and ``tokens[k+1]``.  Leading
    and trailing whitespace is preserved as entries in *tokens* (empty strings when the
    line starts/ends with a separator), so reconstruction is lossless for round-tripping.

    We use this instead of ``str.split`` because we want to be able to re-join with the
    original separators when we hand rows back in a new order.
    """
    tokens: List[str] = []
    seps: List[str] = []
    i = 0
    n = len(line)
    while i < n:
        # Consume a run of non-whitespace.
        j = i
        while j < n and not line[j].isspace():
            j += 1
        tokens.append(line[i:j])
        if j == n:
            break
        # Consume a run of whitespace as a separator.
        k = j
        while k < n and line[k].isspace():
            k += 1
        seps.append(line[j:k])
        i = k
    return tokens, seps


def sort_lines_by_column(
    lines: Sequence[str],
    column_index: int,
    *,
    descending: bool = False,
) -> List[str]:
    """Return *lines* sorted by the column at *column_index* (0-based).

    *column_index* is a 0-based token index into each line, where tokens are delimited by
    runs of whitespace.  Rows that lack a token at that index are treated as "less than" all
    rows that have one when *descending* is False (and therefore come last when
    *descending* is True).

    The sort is stable: rows with identical keys retain their original order.

    Returns a new list; *lines* is not modified.  Each returned line is the original line's
    tokens joined by a single space, which means trailing/leading whitespace is dropped and
    inter-column runs collapse to one space.  See the module docstring for why.
    """
    if not isinstance(column_index, int) or isinstance(column_index, bool):
        raise TypeError("column_index must be an int")
    if column_index < 0:
        raise ValueError("column_index must be non-negative")

    def key(line: str):
        tokens, _seps = _split_preserving(line)
        if column_index >= len(tokens):
            # Missing data sorts first when ascending, last when descending.
            # We return (0, "") so the comparison tuple's second element is never read
            # for a missing row, and so missing rows always sort below present rows.
            return (0, "")
        return (1, tokens[column_index])

    ordered = sorted(lines, key=key, reverse=descending)
    result: List[str] = []
    for line in ordered:
        tokens, _seps = _split_preserving(line)
        result.append(" ".join(tokens))
    return result
