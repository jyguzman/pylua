from typing import Any, Dict


class Env:
    def __init__(self):
        self.level: int = -1
        self.symbol_table: Dict[int, dict] = {}

    def __repr__(self):
        return str(self.symbol_table)

    def get(self, name: str):
        level = self.get_level_of_symbol(name)
        return None if level == -1 else self.symbol_table[level][name]

    def set(self, name: str, val: Any, is_local: bool = True):
        if is_local:
            self.symbol_table[self.level][name] = val
            return
        level = self.get_level_of_symbol(name)
        if level != -1:
            self.symbol_table[level][name] = val
            return
        self.symbol_table[0][name] = val

    def get_level_of_symbol(self, name: str):
        for level in range(self.level, -1, -1):
            if name in self.symbol_table[level]:
                return level
        return -1

    def add_level(self):
        self.level += 1
        self.symbol_table[self.level] = {}

    def pop_level(self):
        if self.level > 0:
            del self.symbol_table[self.level]
            self.level -= 1

    def has_symbol(self, name: str):
        return self.get_level_of_symbol(name) != -1
