import os
import ply.yacc as yacc
import ply.lex as lex



literals = ['=', '+', '-', '*', '/', '(', ')']
reserved = { 
    'int' : 'INTDEC',
    'float' : 'FLOATDEC',
    'print' : 'PRINT'
 }

tokens = [
    'INUMBER', 'FNUMBER', 'NAME'
] + list(reserved.values())


# Tokens

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'NAME')    # Check for reserved words
    return t

def t_FNUMBER(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_INUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Parsing rules

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)

# dictionary of names
names = {}
abstractTree = []

class Node:
    val = ''
    type = ''
    childrens = []

    def __init__( self, val, type, childrens):
        self.val=val
        self.type=type
        self.childrens=childrens

def p_statement_declare_int(p):
    '''statement : INTDEC NAME is_assing
    '''
    if type(p[3]) == float:
        print('No puedes asignar flotantes a enteros')
    else:
        variable = Node(p[2], 'INT', [])
        n = Node(p[3],'=',[variable, p[3]])
        abstractTree.append(n)
        #names[p[2]] = { "type": "INT", "value":p[3]}

def p_is_assing(p):
    '''is_assing : "=" expression 
                | '''
    #p[0]= 0
    n=Node(0,'INT', [])
    if len(p) > 2:
        p[0].type = p[2].type
        p[0].val=p[2].val + p[3].val
        p[0].childrens = p[2]
        #p[0] = p[2]

def p_statement_declare_float(p):
    'statement : FLOATDEC NAME is_assing'
    names[p[2]] = { "type": "FLOAT", "value":p[3]}


def p_statement_print(p):
    '''statement : PRINT '(' expression ')' '''
    print(p[3])

def p_statement_assign(p):
    'statement : NAME "=" expression'
    if p[1] not in names:
        print ( "You must declare a variable before using it")
    names[p[1]]["value"] = p[3]


def p_statement_expr(p):
    'statement : expression'
    # print(p[1])


def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]


def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_inumber(p):
    "expression : INUMBER"
    #p[0] = p[1]
    p[0] = Node(p[1],'INT',[])


def p_expression_fnumber(p):
    "expression : FNUMBER"
    p[0] = p[1]


def p_expression_name(p):
    "expression : NAME"
    try:
        p[0] = names[p[1]]["value"]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    if p:
        print(p)
        print("Syntax error at line '%s' character '%s'" % (p.lexpos, p.lineno) )
    else:
        print("Syntax error at EOF")


if os.path.exists("code.txt") :
    filesize = os.path.getsize("code.txt")
    if filesize == 0:
        print("The file is empty")
    else:
        parser = yacc.yacc()
        input = open('code.txt', 'r').read().split('\n')
        for line in input:
            yacc.parse(line)
else:
    print("File does not exist.")

'''
while True:
    try:
        s = input('calc > ')
    except EOFError:
        break
    if not s:
        continue
    yacc.parse(s)'''