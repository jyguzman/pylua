import Ast
from lexer import Lexer
from parser import Parser
from env import Env

if __name__ == '__main__':
    tokens = Lexer().lex("""
    i = 0
    p = 50
    while i < 10 do
        local k = 2
        i = i + k
    end
    if i >= 10 then
        local k = 5
        i = i + k
    else
        m = 100
    end
    function square(n)
        return n * n
    end
    function add(a, b)
        return a + b
    end
    res = square(5)
    res_two = square(10)
    added = add(#"size", 5)
    j = #("size".."size")
    """)
    print('\n'.join([str(t) for t in tokens]))
    parser = Parser(tokens=tokens)
    program = parser.parse_program()
    visitor = Ast.Visitor(Env())
    print(program.accept(visitor))
    print(visitor.env)

