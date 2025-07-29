"""Standalone abbreviation detection extracted and adapted from scispacy.

The public API mirrors the original functions/classes so existing code that imported
`scispacy.abbreviation` can be migrated by simply changing the import path:

```python
from unv_scispacy_abbr import AbbreviationDetector, find_abbreviation, filter_matches
```
"""
from .abbreviation import (
    AbbreviationDetector,
    find_abbreviation,
    filter_matches,
)

__all__ = [
    "AbbreviationDetector",
    "find_abbreviation",
    "filter_matches",
]
