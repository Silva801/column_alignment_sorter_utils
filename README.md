# column_alignment_sorter_utils

Sorts lines of whitespace-aligned text by a 0-based column index, returning a new list with
rows in order.  Tokens are delimited by runs of whitespace; rows missing the requested
column sort first (ascending) or last (descending).

## Usage

```python
from column_alignment_sorter_utils import sort_lines_by_column

lines = [
    "apple   3 ripe",
    "banana  1 green",
    "cherry  2 red",
]

sorted_lines = sort_lines_by_column(lines, 1)
print("\n".join(sorted_lines))
# banana 1 green
# cherry 2 red
# apple 3 ripe

sorted_desc = sort_lines_by_column(lines, 1, descending=True)
```

`sort_lines_by_column(lines, column_index, *, descending=False)` returns a `list[str]`.
It does not mutate `lines`.

## Why this exists

When you want to re-order aligned text by one column without reaching for `awk`, `sort -k`
and its flags, or a spreadsheet.  The trade-off: rows are split on whitespace runs and
re-joined with single spaces, so inter-column alignment is *not* preserved after sorting.
If you need pixel-perfect column re-alignment, pipe the output through `column -t` or your
alignment tool of choice.  This library handles the sort step only, deliberately.

Numeric-looking values are compared as strings: `"10"` sorts before `"2"`.  Parsing numbers
is a separate concern and doing it implicitly would surprise callers who expect textual
order.

## Awkward edges

* Rows shorter than `column_index` are treated as "missing" data: they sort first when
  ascending and last when descending.
* Tabs are whitespace, so `"a\tb"` is two columns.
* Leading and trailing whitespace on a line is dropped in the output (the line is rebuilt
  from its tokens).

## Layout

```
src/column_alignment_sorter_utils/
  __init__.py   re-exports sort_lines_by_column
  core.py       implementation
```

Tests run under `python -m unittest discover -s tests` with `PYTHONPATH=src`.
