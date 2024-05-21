from Ast import Identifier
from Token import Token, TokenType
from lexer import Lexer
from parser import Parser

if __name__ == '__main__':
    tokens = Lexer().lex("""
    function add(a, b)
        return a + b
    end
    i = 4
    while i < 10 do
        b = add(i, 2)
    end
    sayHi = function() 
        print("Hi!")
    end
    """)
    print('\n'.join([str(t) for t in tokens]))
    parser = Parser(tokens=tokens)
    print(str(parser.parse_program()))
