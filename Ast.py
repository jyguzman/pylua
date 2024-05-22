from Token import Token
from typing import Any, List, Union, Deque
from env import Env
from collections import deque


class Node:
    def accept(self, visitor: 'Visitor'):
        raise NotImplementedError(f"accept() not implemented for {self.__class__.__name__}")


class Statement(Node):
    pass


class Expression(Node):
    pass


class Identifier(Node):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'Identifier({self.name})'

    def accept(self, visitor: 'Visitor' = None):
        return visitor.visit_identifier(self)


class Chunk(Node):
    def __init__(self, statements: Union[List[Statement], Deque[Statement]]):
        self.statements = statements
        if isinstance(self.statements, List):
            self.statements = deque(statements)

    def __repr__(self):
        return '[' + ', '.join([str(s) for s in self.statements]) + ']'

    def accept(self, visitor: 'Visitor'):
        pass


class Block(Chunk):
    def accept(self, visitor: 'Visitor'):
        return visitor.visit_block(self)


class Program(Node):
    def __init__(self, block: List[Block]):
        self.blocks = block

    def __repr__(self):
        return '\n'.join([str(b) for b in self.blocks])

    def accept(self, visitor: 'Visitor'):
        for block in self.blocks:
            block.accept(visitor)


class AssignStatement(Statement):
    def __init__(self, ident: Identifier, value: Expression, is_local: bool):
        self.ident = ident
        self.name = ident.name
        self.value = value
        self.is_local = is_local

    def __repr__(self):
        return f'Assignment({self.ident}, {self.value}, local: {self.is_local})'

    def accept(self, visitor: 'Visitor'):
        visitor.visit_assignment(self)


class ReturnStatement(Statement):
    def __init__(self, value: Expression):
        self.value = value

    def __repr__(self):
        return f'ReturnStmt({self.value})'

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_return_statement(self)


class IfStatement(Statement):
    def __init__(self, condition: Expression, true_block: Block, else_block: Block = None):
        self.condition = condition
        self.true_block = true_block
        self.else_block = else_block

    def __repr__(self):
        return f'IfStmt({self.condition}, {self.true_block}, {self.else_block})'

    def accept(self, visitor: 'Visitor'):
        visitor.visit_if_stmt(self)


class WhileLoop(Statement):
    def __init__(self, condition: Expression, body: Block):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f'WhileLoop({self.condition}, {self.body})'

    def accept(self, visitor: 'Visitor'):
        visitor.visit_while_loop(self)


class ForLoop(Statement):
    def __init__(self, initializer: AssignStatement, stop: Expression, step: Expression, body: Block):
        self.initializer = initializer
        self.stop = stop
        self.step = step
        self.body = body

    def __repr__(self):
        return f'ForLoop({self.initializer}, {self.stop}, {self.step}, {self.body})'

    def accept(self, visitor: 'Visitor'):
        visitor.visit_for_loop(self)


class Literal(Expression):
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return f'Literal({self.value})'

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_literal(self)


class BinaryExpr(Expression):
    def __init__(self, left: Expression, op: Token, right: Expression):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f'Binary({self.left}, {self.op.token_type}, {self.right})'

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_binary_expr(self)


class UnaryExpr(Expression):
    def __init__(self, op: Token, operand: Expression):
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f'Unary({self.op.token_type}, {self.operand})'

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_unary_expression(self)


class GroupedExpr(Expression):
    def __init__(self, inner: Expression):
        self.inner = inner

    def __repr__(self):
        return f'Grouping({self.inner})'

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_grouped_expression(self)


class Function(Expression, Statement):
    def __init__(self, params: List[str], body: Block, name: str = None, is_local: bool = False):
        self.params = params
        self.body = body
        self.name = name
        self.is_local = is_local

    def __repr__(self):
        return f'Function({self.name}, {self.params}, {self.body})'

    def accept(self, visitor: 'Visitor'):
        visitor.visit_function_def(self)


class FunctionCall(Expression, Statement):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args

    def __repr__(self):
        args_str = ', '.join([str(a) for a in self.args])
        return f'{self.__class__.__name__}({self.name}, {args_str})'

    def accept(self, visitor: 'Visitor'):
        return visitor.visit_function_call(self)


class Visitor:
    def __init__(self, env: Env = Env()):
        self.env = env

    @staticmethod
    def visit_literal(le: Literal) -> Any:
        return le.value

    def visit_grouped_expression(self, ge: GroupedExpr):
        return ge.inner.accept(self)

    def visit_binary_expr(self, expr: BinaryExpr):
        left, op, right = expr.left, expr.op.lexeme, expr.right
        if op in ('+', '-', '*',  '/', '%'):
            left = left.accept(self)
            right = right.accept(self)

            if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
                print(f"Operands for '{op} must be of type number")
                exit(1)

            return {
                '+': left + right,
                '-': left - right,
                '*': left * right,
                '/': left + right,
                '%': left % right,
            }[op]

        if op in ('==', '~=', '<', '<=', '>', '>='):
            left = left.accept(self)
            right = right.accept(self)

            if not isinstance(left, (int, float, str)) or not isinstance(right, (int, float, str)):
                print(f"Operands for '{op}' must be of type number or string")
                exit(1)

            if type(left) is not type(right):
                print(f"Operands for '{op}' must be both of type number or string")
                exit(1)

            return {
                '==': left == right,
                '~=': left != right,
                '<': left < right,
                '<=': left <= right,
                '>': left > right,
                '>=': left >= right
            }[op]

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

            if left in (None, False) or right in (None, False):
                return False
            return True

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
            return False if operand in (True, None) else True

        print(f"Unrecognized unary operator '{op}'")
        exit(1)

    def visit_assignment(self, stmt: AssignStatement):
        self.env.set(stmt.name, stmt.value.accept(self), stmt.is_local)

    def visit_return_statement(self, rs: ReturnStatement):
        return rs.value.accept(self)

    def visit_identifier(self, ident: Identifier):
        value = self.env.get(ident.name)
        if value is None:
            print(f"Identifier {ident.name} not previously declared")
            exit(1)
        return value

    def visit_block(self, block: Block):
        self.env.add_level()
        return_value = None
        for stmt in block.statements:
            if isinstance(stmt, ReturnStatement):
                return_value = stmt.accept(self)
                break
            stmt.accept(self)
        self.env.pop_level()
        return return_value

    def visit_while_loop(self, wl: WhileLoop):
        condition_result = wl.condition.accept(self)
        while condition_result:
            wl.body.accept(self)
            condition_result = wl.condition.accept(self)

    def visit_for_loop(self, fl: ForLoop):
        pass

    def visit_if_stmt(self, if_stmt: IfStatement):
        condition_result = if_stmt.condition.accept(self)

        if condition_result:
            if_stmt.true_block.accept(self)
            return

        if if_stmt.else_block is not None:
            if_stmt.else_block.accept(self)

    def visit_function_def(self, fn: Function):
        if fn.name is None:
            return fn
        self.env.set(fn.name, fn, fn.is_local)
        return fn

    def visit_function_call(self, fc: FunctionCall):
        fn: Function = self.env.get(fc.name)

        if fn is None:
            print(f"Function '{fc.name}' not previously declared")
            exit(1)

        if len(fc.args) != len(fn.params):
            print(f"Incorrect number of arguments for '{fc.name}'")
            exit(1)

        args, params = fc.args, fn.params
        body = fn.body.statements.copy()
        for i in range(len(args)):
            body.appendleft(AssignStatement(Identifier(params[i]), args[i], True))

        return Block(body).accept(self)

