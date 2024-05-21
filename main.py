from Ast import Identifier
from Token import Token, TokenType
from lexer import Lexer
from parser import Parser

if __name__ == '__main__':
    lexer = Lexer()
    tokens = lexer.lex("""
    5 * (2 + 3) and not true
    """)
    print('\n'.join([str(t) for t in tokens]))
    source = "5 * (2 + 3) and not #\"true\""
    parser = Parser(source)
    print(parser.parse_expression())
