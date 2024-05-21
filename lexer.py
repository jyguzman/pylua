from Token import TokenType, Token
from typing import List


class Lexer:
    def __init__(self, source: str = ""):
        self.source = source
        self.pos: int = 0
        self.line: int = 0
        self.col: int = 0
        self.tokens: List[Token] = []
        self.keywords = {
            'function': TokenType.FUNCTION,
            'return': TokenType.RETURN,
            'val': TokenType.VAL,
            'local': TokenType.LOCAL,
            'for': TokenType.FOR,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'while': TokenType.WHILE,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'end': TokenType.END,
            'if': TokenType.IF,
            'elseif': TokenType.ELSEIF,
            'do': TokenType.DO
        }

    def is_eof(self):
        return True if self.pos >= len(self.source) else False

    def peek(self, n=0):
        if self.pos + n >= len(self.source):
            return '\0'
        return self.source[self.pos + n]

    def advance(self):
        self.pos += 1
        if self.is_eof():
            return '\0'

        curr = self.peek()
        if curr == '\n':
            self.col = 0
            self.line += 1
        else:
            self.col += 1

        return self.source[self.pos]

    def lex_string(self):
        lexeme = []
        start_col = self.col
        start_line = self.line

        c = self.advance()
        while c != '\"':
            lexeme.append(c)
            c = self.advance()

        lexeme = ''.join(lexeme)
        self.advance()
        return Token(self.pos, start_line, start_col, TokenType.STRING, lexeme, f'"{lexeme}"')

    def lex_ident(self):
        lexeme = []
        start_col = self.col
        start_line = self.line

        c = self.peek()
        while c.isalpha() or c in ('_', '-'):
            lexeme.append(c)
            c = self.advance()

        lexeme = ''.join(lexeme)
        token_type = TokenType.IDENT if lexeme not in self.keywords else self.keywords[lexeme]
        literal = None
        if token_type in (TokenType.TRUE, TokenType.FALSE):
            literal = True if token_type == TokenType.TRUE else False
        return Token(self.pos, start_line, start_col, token_type, lexeme, literal)

    def lex_number(self):
        lexeme = []
        start_col = self.col
        start_line = self.line
        is_float = False

        c = self.peek()
        while c.isdigit() or c == '.':
            if c == '.':
                is_float = True
            lexeme.append(c)
            c = self.advance()

        lexeme = ''.join(lexeme)
        number = float(lexeme) if is_float else int(lexeme)
        return Token(self.pos, start_line, start_col, TokenType.NUMBER, lexeme, number)

    def match(self):
        if self.is_eof():
            return Token(self.pos, self.line, self.col, TokenType.EOF, '', None)

        c = self.peek()
        token = Token(self.pos, self.line, self.col, TokenType.EOF, '', None)

        if c == ' ':
            self.advance()
            return self.match()
        elif c in ('\n', '\r'):
            while self.peek() in ('\n', '\r'):
                self.advance()
            if self.is_eof():
                return Token(self.pos, self.line, self.col, TokenType.EOF, '\0', None)
            else:
                return self.match()
        elif c.isdigit():
            return self.lex_number()
        elif c.isalpha():
            return self.lex_ident()
        elif c == '"':
            return self.lex_string()
        elif c == ',':
            token = Token(self.pos, self.line, self.col, TokenType.COMMA, ',', None)
            self.advance()
        elif c == ';':
            token = Token(self.pos, self.line, self.col, TokenType.SEMI, ';', None)
            self.advance()
        elif c == '#':
            token = Token(self.pos, self.line, self.col, TokenType.HASHTAG, '#', None)
            self.advance()
        elif c == '.':
            if self.peek(1) == '.':
                self.advance()
                token = Token(self.pos, self.line, self.col, TokenType.DOTDOT, '..', None)
            else:
                print(f'Unrecognized token {c}')
                exit(1)
            self.advance()
        elif c == '<':
            if self.peek(1) == '=':
                self.advance()
                token = Token(self.pos, self.line, self.col, TokenType.LEQ, '<=', None)
            else:
                token = Token(self.pos, self.line, self.col, TokenType.LESS, '<', None)
            self.advance()
        elif c == '>':
            if self.peek(1) == '=':
                self.advance()
                token = Token(self.pos, self.line, self.col, TokenType.GEQ, '>=', None)
            else:
                token = Token(self.pos, self.line, self.col, TokenType.GREATER, '>', None)
            self.advance()
        elif c == '=':
            if self.peek(1) == '=':
                self.advance()
                token = Token(self.pos, self.line, self.col, TokenType.EQUALS, '==', None)
            else:
                token = Token(self.pos, self.line, self.col, TokenType.ASSIGN, '=', None)
            self.advance()
        elif c == '~':
            if self.peek(1) == '=':
                self.advance()
                token = Token(self.pos, self.line, self.col, TokenType.NEQ, '~=', None)
            else:
                print(f'Unrecognized token {c}')
                exit(1)
            self.advance()
        elif c == '+':
            token = Token(self.pos, self.line, self.col, TokenType.PLUS, '+', None)
            self.advance()
        elif c == '-':
            if self.peek(1) == '-':
                while c != '\n':
                    self.advance()
                return self.match()
            else:
                token = Token(self.pos, self.line, self.col, TokenType.MINUS, '-', None)
            self.advance()
        elif c == '*':
            token = Token(self.pos, self.line, self.col, TokenType.STAR, '*', None)
            self.advance()
        elif c == '/':
            token = Token(self.pos, self.line, self.col, TokenType.SLASH, '/', None)
            self.advance()
        elif c == '%':
            token = Token(self.pos, self.line, self.col, TokenType.PERCENT, '%', None)
            self.advance()
        elif c == '(':
            token = Token(self.pos, self.line, self.col, TokenType.LPAREN, '(', None)
            self.advance()
        elif c == ')':
            token = Token(self.pos, self.line, self.col, TokenType.RPAREN, ')', None)
            self.advance()
        elif c == '{':
            token = Token(self.pos, self.line, self.col, TokenType.LBRACE, '{', None)
            self.advance()
        elif c == '}':
            token = Token(self.pos, self.line, self.col, TokenType.RBRACE, '}', None)
            self.advance()
        elif c == '[':
            token = Token(self.pos, self.line, self.col, TokenType.LBRACKET, '[', None)
            self.advance()
        elif c == ']':
            token = Token(self.pos, self.line, self.col, TokenType.RBRACKET, ']', None)
            self.advance()
        else:
            print(f'Unrecognized token {c}')
            exit(1)

        return token

    def lex(self, source=''):
        if source:
            self.source = source
            self.line = 1
            self.col = 1
            self.pos = 0
            self.tokens.clear()

        while not self.is_eof():
            token = self.match()
            self.tokens.append(token)

        if self.tokens[-1].token_type != TokenType.EOF:
            self.tokens.append(Token(self.pos, self.line, self.col, TokenType.EOF, '\0', None))

        return self.tokens


if __name__ == "__main__":
    lexer = Lexer()
    print(lexer.lex("+-/~=23.4"))
