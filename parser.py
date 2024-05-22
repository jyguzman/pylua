from Token import TokenType, Token
from lexer import Lexer
from typing import List
import Ast


class Parser:
    def __init__(self, source: str = None, tokens: List[Token] = None):
        if source is not None and tokens is not None:
            print('Parser requires either source string of list of tokens, not both.')
            exit(1)

        if source is not None:
            self.tokens = Lexer(source).lex()

        if tokens is not None:
            self.tokens = tokens

        self.pos: int = 0

    def peek(self, n=0):
        return self.tokens[self.pos + n]

    def previous(self):
        return self.peek(-1)

    def is_eof(self):
        return self.peek().token_type == TokenType.EOF

    def advance(self):
        if self.is_eof():
            return self.peek()

        token = self.peek()
        self.pos += 1
        return token

    def accept(self, *token_types: TokenType):
        return self.peek().token_type in token_types

    def expect(self, token_type: TokenType):
        t = self.peek()
        if self.accept(token_type):
            self.advance()
        else:
            print(f'Expected token of type {token_type} at line:column {t.line}:{t.col}')
            exit(1)

    def parse_identifier(self):
        return Ast.Identifier(self.peek())

    def parse_expression(self) -> Ast.Expression:
        return self.parse_or()

    def parse_or(self):
        expr = self.parse_and()
        while self.accept(TokenType.OR):
            op = self.advance()
            right = self.parse_or()
            expr = Ast.BinaryExpr(expr, op, right)
        return expr

    def parse_and(self):
        expr = self.parse_equality()
        while self.accept(TokenType.AND):
            op = self.advance()
            right = self.parse_equality()
            expr = Ast.BinaryExpr(expr, op, right)
        return expr

    def parse_equality(self):
        expr = self.parse_comparison()
        while self.accept(TokenType.NEQ, TokenType.EQUALS):
            op = self.advance()
            right = self.parse_comparison()
            expr = Ast.BinaryExpr(expr, op, right)
        return expr

    def parse_comparison(self):
        expr = self.parse_term()
        while self.accept(TokenType.GREATER, TokenType.GEQ, TokenType.LESS, TokenType.LEQ):
            op = self.advance()
            right = self.parse_term()
            expr = Ast.BinaryExpr(expr, op, right)
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.accept(TokenType.PLUS, TokenType.MINUS, TokenType.DOTDOT):
            op = self.advance()
            right = self.parse_factor()
            expr = Ast.BinaryExpr(expr, op, right)
        return expr

    def parse_factor(self):
        expr = self.parse_unary()
        while self.accept(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.advance()
            right = self.parse_unary()
            expr = Ast.BinaryExpr(expr, op, right)
        return expr

    def parse_unary(self):
        if self.accept(TokenType.NOT, TokenType.HASHTAG, TokenType.MINUS):
            op = self.advance()
            expr = self.parse_unary()
            return Ast.UnaryExpr(op, expr)
        return self.parse_primary()

    def parse_primary(self):
        if self.accept(TokenType.NUMBER, TokenType.STRING,
                       TokenType.FALSE, TokenType.TRUE):
            return Ast.Literal(self.advance().literal)
        elif self.accept(TokenType.IDENT):
            if self.peek(1).token_type == TokenType.LPAREN:
                return self.parse_function_call()
            return Ast.Identifier(self.advance())
        elif self.accept(TokenType.LPAREN):
            self.advance()
            expr = Ast.GroupedExpr(self.parse_expression())
            self.expect(TokenType.RPAREN)
            return expr
        elif self.accept(TokenType.FUNCTION):
            return self.parse_function_def()
        else:
            print(f'Invalid token {self.peek()}')
            exit(1)

    def parse_function_def(self) -> Ast.Function:
        self.expect(TokenType.FUNCTION)
        name = ''
        if self.accept(TokenType.IDENT):
            name = self.advance().lexeme

        self.expect(TokenType.LPAREN)
        params = []
        while not self.accept(TokenType.RPAREN):
            self.expect(TokenType.IDENT)
            params.append(self.previous().lexeme)
            if not self.accept(TokenType.RPAREN):
                self.expect(TokenType.COMMA)
        self.expect(TokenType.RPAREN)

        body = self.parse_block()
        self.expect(TokenType.END)
        return Ast.Function(name, params, body)

    def parse_function_call(self) -> Ast.FunctionCall:
        self.expect(TokenType.IDENT)
        name = self.previous().lexeme

        self.expect(TokenType.LPAREN)
        args = []
        while not self.accept(TokenType.RPAREN):
            args.append(self.parse_expression())
            if not self.accept(TokenType.RPAREN):
                self.expect(TokenType.COMMA)
        self.expect(TokenType.RPAREN)

        return Ast.FunctionCall(name, args)

    def parse_program(self) -> Ast.Program:
        blocks = []
        while not self.is_eof():
            blocks.append(self.parse_block())
        return Ast.Program(blocks)

    def parse_block(self) -> Ast.Block:
        statements = []
        while not self.accept(TokenType.ELSE, TokenType.END, TokenType.EOF):
            statements.append(self.parse_statement())
        return Ast.Block(statements)

    def parse_statement(self) -> Ast.Statement:
        if self.accept(TokenType.LOCAL):
            return self.parse_assignment()
        if self.accept(TokenType.IDENT):
            if self.peek(1).token_type == TokenType.LPAREN:
                return self.parse_function_call()
            return self.parse_assignment()
        if self.accept(TokenType.RETURN):
            return self.parse_return_statement()
        if self.accept(TokenType.WHILE):
            return self.parse_while_loop()
        if self.accept(TokenType.FOR):
            return self.parse_for_loop()
        if self.accept(TokenType.IF):
            return self.parse_if_statement()
        if self.accept(TokenType.FUNCTION):
            return self.parse_function_def()
        return self.parse_expression_statement()

    def parse_expression_statement(self):
        return Ast.ExpressionStatement(self.parse_expression())

    def parse_if_statement(self) -> Ast.IfStatement:
        self.expect(TokenType.IF)
        condition = self.parse_expression()

        self.expect(TokenType.THEN)
        true_block = self.parse_block()

        else_block = None
        if self.accept(TokenType.ELSE):
            self.expect(TokenType.ELSE)
            else_block = self.parse_block()

        self.expect(TokenType.END)

        return Ast.IfStatement(condition, true_block, else_block)

    def parse_while_loop(self) -> Ast.WhileLoop:
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()

        self.expect(TokenType.DO)
        body = self.parse_block()

        self.expect(TokenType.END)

        return Ast.WhileLoop(condition, body)

    def parse_for_loop(self) -> Ast.ForLoop:
        self.expect(TokenType.FOR)
        initializer = self.parse_assignment(is_local=True)

        self.expect(TokenType.COMMA)
        stop = self.parse_expression()

        step = 1
        if self.accept(TokenType.COMMA):
            self.expect(TokenType.COMMA)
            step = self.parse_expression()

        self.expect(TokenType.DO)
        body = self.parse_block()

        self.expect(TokenType.END)

        return Ast.ForLoop(initializer, stop, step, body)

    def parse_assignment(self, is_local=False) -> Ast.AssignStatement:
        if self.accept(TokenType.LOCAL):
            is_local = True
            self.advance()

        self.expect(TokenType.IDENT)
        ident = Ast.Identifier(self.previous())

        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()

        return Ast.AssignStatement(ident, value, is_local)

    def parse_return_statement(self) -> Ast.ReturnStatement:
        self.expect(TokenType.RETURN)
        value = self.parse_expression()
        return Ast.ReturnStatement(value)
