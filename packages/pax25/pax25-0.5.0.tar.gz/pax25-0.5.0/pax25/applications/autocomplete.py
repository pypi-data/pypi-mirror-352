"""
Trie for auto-complete style lookups. Useful for short commands and help lookups.
"""


class AutocompleteDict[V]:
    """
    An autocomplete dictionary. Lookups return a set of candidate values.

    This is not especially space efficient-- proper refactoring to a true Trie might be
    better if we expect to have a lot of entries.
    """

    def __init__(self) -> None:
        """
        Set up our internal state for Autocomplete lookups.
        """
        self.store: dict[str, V] = {}
        self._lookups: dict[str, set[str]] = {}

    def __setitem__(
        self,
        key: str,
        value: V,
    ) -> None:
        """
        Add an entry and populate its autocomplete lookups.
        """
        existing = False
        if key in self.store:
            existing = True
        self.store[key] = value
        if existing:
            # No need to create the lookups-- they're already here.
            return
        current = ""
        for char in key:
            current += char
            if current in self._lookups:
                self._lookups[current] |= {key}
            else:
                self._lookups[current] = {key}

    def __getitem__(self, key: str) -> set[tuple[str, V]]:
        """
        Get a key from the AutoComplete dict.
        """
        # Pull exact matches immediately.
        if key in self.store:
            return {(key, self.store[key])}
        if key not in self._lookups:
            raise KeyError(key)
        return {(value, self.store[value]) for value in self._lookups[key]}

    def __delitem__(self, key: str) -> None:
        """
        Remove a key from the AutoComplete dict.
        """
        if key not in self.store:
            raise KeyError(key)
        del self.store[key]
        current = ""
        for char in key:
            current += char
            self._lookups[current] -= {key}
            if not self._lookups[current]:
                del self._lookups[current]
