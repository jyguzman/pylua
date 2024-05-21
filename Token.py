from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    # punctuation
    SEMI = 'SEMICOLON'
    COMMA = 'COMMA'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'

    # unary operators
    NOT = 'NOT'
    HASHTAG = 'HASHTAG'

    # binary operators
    PLUS = 'PLUS'
    STAR = 'STAR'
    DOTDOT = 'DOTDOT'
    SLASH = 'SLASH'
    EQUALS = 'EQUALS'
    NEQ = 'NEQ'
    GREATER = 'GREATER'
    GEQ = 'GEQ'
    LESS = 'LESS'
    LEQ = 'LEQ'
    ASSIGN = 'ASSIGNMENT'
    PERCENT = 'PERCENT'
    AND = 'AND'
    OR = 'OR'

    # unary or binary
    MINUS = 'MINUS'

    # types
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    NIL = 'NIL'

    # keywords
    FUNCTION = 'FUNCTION'
    RETURN = 'RETURN'
    VAL = 'VAL'
    LOCAL = 'LOCAL'
    FOR = 'FOR'
    DO = 'DO'
    END = 'END'
    IF = 'IF'
    ELSEIF = 'ELSEIF'
    WHILE = 'WHILE'
    THEN = 'THEN'
    ELSE = 'ELSE'

    IDENT = 'IDENT'

    EOF = 'EOF'


@dataclass
class Token:
    """pos, line, col, token_type, lexeme, literal"""
    pos: int
    line: int
    col: int
    token_type: TokenType
    lexeme: str
    literal: Any

    def __str__(self):
        literal_str = ')'
        if self.literal:
            literal_str = f', literal: {self.literal})'
        return f"Token({self.token_type}, line: {self.line}, col: {self.col}, pos: {self.pos}, lexeme: {self.lexeme}" + literal_str
