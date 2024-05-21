from env import Env
from Ast import Node
from typing import Any


class Visitor:
    def __init__(self, env: Env = Env({})):
        self.env = env

    def visit(self, node: Node) -> Any:
        return node.accept(self)