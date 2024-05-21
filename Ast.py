from Token import Token
from typing import Any, List
from env import Env


class Node:
    def accept(self, visitor: 'Visitor'):
        pass


class Statement(Node):
    pass


class Expression(Node):
    pass


class Identifier(Node):
    def __init__(self, token: Token):
        self.token = token

    def __str__(self):
        return f'Ident({self.token.lexeme})'

    def accept(self, visitor: 'Visitor' = None):
        return self.token.lexeme


class Chunk(Node):
    def __init__(self, statements: List[Statement]):
        self.statements = statements

    def __str__(self):
        return ', '.join([str(stmt) for stmt in self.statements])


class Block(Chunk):
    pass


class Program(Node):
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks


class AssignStatement(Statement):
    def __init__(self, ident: Identifier, value: Expression, is_local: bool):
        self.ident = ident
        self.value = value
        self.is_local = is_local

    def __str__(self):
        return f'Assignment({str(self.ident)}, {str(self.value)}, local: {self.is_local})'


class ReturnStatement:
    def __init__(self, value: Expression):
        self.value = value

    def __str__(self):
        return f'ReturnStmt({str(self.value)})'


class IfStatement(Statement):
    def __init__(self, condition: Expression, true_block: Block, else_block: Block = None):
        self.condition = condition
        self.true_block = true_block
        self.else_block = else_block

    def __str__(self):
        return f'IfStmt({str(self.condition)}, {str(self.true_block)}, {str(self.else_block)})'


class WhileLoop(Statement):
    def __init__(self, condition: Expression, body: Block):
        self.condition = condition
        self.body = body

    def __str__(self):
        return f'WhileLoop({str(self.condition)}, {str(self.body)})'


class ForLoop(Statement):
    def __init__(self, initializer: AssignStatement, stop: Expression, step: Expression, body: Block):
        self.initializer = initializer
        self.stop = stop
        self.step = step
        self.body = body

    def __str__(self):
        return f'ForLoop({str(self.initializer)}, {str(self.stop)}, {str(self.step)}, {str(self.body)})'


class Literal(Expression):
    def __init__(self, value: Any):
        self.value = value

    def __str__(self):
        return f'Literal({self.value})'

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_literal(self)


class BinaryExpr(Expression):
    def __init__(self, left: Expression, op: Token, right: Expression):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f'Binary({self.left}, {self.op.token_type}, {self.right})'


class UnaryExpr(Expression):
    def __init__(self, op: Token, operand: Expression):
        self.op = op
        self.operand = operand

    def __str__(self):
        return f'Unary({self.op.token_type}, {self.operand})'


class GroupedExpr(Expression):
    def __init__(self, expr: Expression):
        self.expr = expr

    def __str__(self):
        return f'Grouping({str(self.expr)})'


class FunctionExpr(Expression):
    def __init__(self, name: str, params: List[str], body: Block):
        self.name = name
        self.params = params
        self.body = body

    def __str__(self):
        return f'Function({self.name}, {self.params}, {self.body})'


class FunctionCallExpr(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args

    def __str__(self):
        return f'FunCall({self.name}, {self.args})'


class Visitor:
    def __init__(self, env: Env = Env({})):
        self.env = env

    @staticmethod
    def visit_literal(literal: Literal) -> Any:
        return literal.value

    def visit_binary_expr(self, expr: BinaryExpr):
        pass

