from Token import Token
from typing import Any, List
from env import Env


class Node:
    def accept(self, visitor: 'Visitor'):
        if self is None:
            print("Calling accept on null node")
            exit(1)
        pass


class Statement(Node):
    pass


class Expression(Node):
    def accept(self, visitor: 'Visitor'):
        pass


class Identifier(Node):
    def __init__(self, token: Token):
        self.token = token
        self.name = token.lexeme

    def __str__(self):
        return f'Ident({self.name})'

    def accept(self, visitor: 'Visitor' = None):
        return visitor.visit_identifier(self)


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

    def __str__(self):
        return '\n'.join([str(c) for c in self.chunks])


class ExpressionStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr = expr

    def __str__(self):
        return f'ExprStmt({str(self.expr)})'


class AssignStatement(Statement):
    def __init__(self, ident: Identifier, value: Expression, is_local: bool):
        self.ident = ident
        self.name = ident.token.lexeme
        self.value = value
        self.is_local = is_local

    def __str__(self):
        return f'Assignment({str(self.ident)}, {str(self.value)}, local: {self.is_local})'


class ReturnStatement(Statement):
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

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_unary_expression(self)


class GroupedExpr(Expression):
    def __init__(self, inner: Expression):
        self.inner = inner

    def __str__(self):
        return f'Grouping({str(self.inner)})'

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_grouped_expression(self)


class Function(Expression, Statement):
    def __init__(self, name: str, params: List[str], body: Block):
        self.name = name
        self.params = params
        self.body = body

    def __str__(self):
        return f'Function({self.name}, {self.params}, {self.body})'


class FunctionCall(Expression, Statement):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args

    def __str__(self):
        args_str = ', '.join([str(a) for a in self.args])
        return f'FunCall({self.name}, {args_str})'


class Visitor:
    def __init__(self, env: Env = Env({})):
        self.env = env

    @staticmethod
    def visit_literal(le: Literal) -> Any:
        return le.value

    def visit_grouped_expression(self, ge: GroupedExpr):
        return ge.inner.accept(self)

    def visit_binary_expr(self, expr: BinaryExpr):
        left, op, right = expr.left, expr.op.lexeme, expr.right
        if op == '+':
            left = left.accept(self)
            right = right.accept(self)

            if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
                print(f"Operands for '{op} must be of type number")
                exit(1)

            return left + right

        if op == '-':
            left = left.accept(self)
            right = right.accept(self)

            if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
                print(f"Operands for '{op} must be of type number")
                exit(1)

            return left - right

        if op == '*':
            left = left.accept(self)
            right = right.accept(self)

            if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
                print(f"Operands for '{op} must be of type number")
                exit(1)

            return left * right

        if op == '/':
            left = left.accept(self)
            right = right.accept(self)

            if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
                print(f"Operands for '{op} must be of type number")
                exit(1)

            return left / right

        if op == '%':
            left = left.accept(self)
            right = right.accept(self)

            if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
                print(f"Operands for '{op} must be of type number")
                exit(1)

            return left % right

        if op == '..':
            left = left.accept(self)
            right = right.accept(self)

            if not isinstance(left, str) or not isinstance(right, str):
                print(f"Operands for '{op} must be of type string")
                exit(1)

            return left + right

        if op == 'and':
            left = left.accept(self)
            right = right.accept(self)

            return left and right

        print(f"Unrecognized binary operator '{op}'")
        exit(1)

    def visit_unary_expression(self, ue: UnaryExpr):
        op = ue.op.lexeme
        operand = ue.operand.accept(self)

        if op == '#':
            if not isinstance(operand, str):
                print("Operand for '#' must be of type string.")
                exit(1)
            return len(operand)

        if op == '-':
            if not isinstance(operand, (int, float)):
                print("Operand for '-' must be of type number.")
                exit(1)
            return -operand

        if op == 'not':
            if operand in (True, None):
                return False
            return True

        print(f"Unrecognized unary operator '{op}'")
        exit(1)

    def visit_assignment(self, stmt: AssignStatement):
        self.env.set(stmt.name, stmt.value.accept(self), stmt.is_local)

    def visit_identifier(self, ident: Identifier):
        value = self.env.get(ident.name)
        if value is None:
            print(f"Identifier {ident.name} not previously declared")
            exit(1)
        return value

    def visit_block(self, block: Block):
        self.env.add_level()
        for stmt in block.statements:
            stmt.accept(self)
        self.env.pop_level()

    def visit_while_loop(self, wl: WhileLoop):
        condition_result = wl.condition.accept(self)
        while condition_result:
            wl.body.accept(self)
            condition_result = wl.condition.accept(self)

    def visit_for_loop(self, fl: ForLoop):
        pass

    def visit_if_stmt(self, ifs: IfStatement):
        condition_result = ifs.condition.accept(self)
        if condition_result:
            ifs.true_block.accept(self)
            return

        if ifs.else_block is not None:
            ifs.else_block.accept(self)
