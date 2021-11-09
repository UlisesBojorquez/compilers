import ply.yacc as yacc
from lexer import tokens, literals
import lexer
import sys

class Node:
    def __init__(self, type, children=None, parent=None, ptype=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = [ ]
        if parent:
            self.parent = parent
        else:
            self.parent = None
        if ptype:
            self.ptype = ptype
        else:
            self.ptype = None

def setParentOfChildren(node):
    for child in node.children:
        child.parent = node

def hasGreaterPrecedence(a, b):
    if(a in "^"):
        return True
    elif(a in "*/" and b in "*/+-"):
        return True
    elif(a in "+-" and b in "+-"):
        return True
    else:
        return False

def treeFromInfix(input):
    #Infix to Postfix
    stack = []
    output = []
    for a in input:
        e = a
        if(e == "("):
            stack.append(e)
        elif(e == ")"):
            while(len(stack)>0 and stack[len(stack)-1] != "("):
                output.append(stack.pop())
            if(stack[len(stack)-1]=="("):
                stack.pop()
            else:
                sys.exit('\033[91m' + "[ ! ] Expresion numerica invalida" + '\033[0m')
        elif(e in "+-/*^"):
            while(len(stack)>0 and hasGreaterPrecedence(stack[len(stack)-1],e)):
                output.append(stack.pop())
            stack.append(e)
        else:
            output.append(e)
    while(len(stack)>0):
        output.append(stack.pop())

    #Postfix to Tree
    stack = []
    input = output
    while(len(input)>0):
        e = input.pop(0)
        if(isinstance(e, Node)):
            stack.append(e)
        elif(e=='('):
            sys.exit('\033[91m' + "[ ! ] Expresion numerica invalida" + '\033[0m')
        elif(e in "+-/*^"):
            if(len(stack)<2):
                sys.exit('\033[91m' + "[ ! ] Expresion numerica invalida" + '\033[0m')
            else:
                a2=stack.pop()
                if(not(isinstance(a2, Node))):
                    a2=Node(a2)
                a1=stack.pop()
                if(not(isinstance(a1, Node))):
                    a1=Node(a1)
                newNode=Node(e,children=[a1,a2])
                setParentOfChildren(newNode)
                stack.append(newNode)
        else:
            stack.append(e)
    if(len(stack) != 1):
        sys.exit('\033[91m' + "[ ! ] Expresion numerica invalida" + '\033[0m')
    else:
        e=stack.pop()
        if(not(isinstance(e, Node))):
            e=Node(e)
        return e

def p_block(p):
    '''
    block : stmt block
        | stmt 
    '''
    if(len(p)>2):
        p[0]=Node('block',children=[p[1],p[2]])
        setParentOfChildren(p[0])
    else:
        p[0]=p[1]

def p_stmt(p):
    '''
    stmt : simpstmt ';'
        | flowctrl
        | stmtprint ';'
    '''
    p[0]=p[1]

def p_simpstmt_assdec_num(p):
    '''
    simpstmt : INT ID '=' numexpr
        | FLOAT ID '=' numexpr
    '''
    d=Node('declaration', [Node(p[2]),Node(p[1])])
    setParentOfChildren(d)
    p[0]=Node('assignment',[d, treeFromInfix(p[4])])
    setParentOfChildren(p[0])

def p_simpstmt_dec(p):
    '''
    simpstmt : INT ID
        | FLOAT ID
    '''
    p[0]=Node('declaration',[Node(p[2]),Node(p[1])])
    setParentOfChildren(p[0])

def p_simpstmt_ass(p):
    '''
    simpstmt : ID '=' expr
    '''
    p[0]=Node('assignment',[Node(p[1]),p[3]])
    setParentOfChildren(p[0])

def p_expr_num(p):
    '''
    expr : numexpr
    '''
    p[0]= treeFromInfix(p[1])

def p_expr_bool(p):
    '''
    expr : boolexpr
    '''
    p[0]= p[1]

def p_flowctrl_if(p):
    '''
    flowctrl : IF '(' boolexpr ')' '{' block '}' elif else
    '''
    if(len(p)>2):
        ch=[p[3],p[6]]
        if(p[8]):
            ch.append(p[8])
        if(p[9]):
            ch.append(p[9])
        p[0]=Node('if',children=ch)
        setParentOfChildren(p[0])

def p_elif(p):
    '''
    elif : ELIF '(' boolexpr ')' '{' block '}' elif
        | empty
    '''
    if(len(p)>2):
        ch=[p[3],p[6]]
        if(p[8]):
            ch.append(p[8])
        p[0]=Node('elif',children=ch)
        setParentOfChildren(p[0])

def p_else(p):
    '''
    else : ELSE '{' block '}'
        | empty
    '''
    if(len(p)>2):
        elseNode=Node('else',[p[3]])
        setParentOfChildren(elseNode)
        p[0] = elseNode
        setParentOfChildren(p[0])

def p_numexpr_num(p):
    '''
    numexpr : num
    '''
    p[0]=p[1]

def p_numexpr_arit(p):
    '''
    numexpr : numexpr arit numexpr
    '''
    p[0] = []
    for i in p[1]:
        p[0].append(i)
    p[0].append(p[2])
    for i in p[3]:
        p[0].append(i)

def p_numexpr_id(p):
    '''
    numexpr : ID '+' numexpr
        | ID '*' numexpr
        | ID '-' numexpr
        | ID '/' numexpr
        | ID '^' numexpr
    '''
    p[0] = []
    p[0].append(p[1])
    p[0].append(p[2])
    for i in p[3]:
        p[0].append(i)

def p_numexpr_par(p):
    '''
    numexpr : '(' numexpr ')'
    '''
    p[0] = []
    p[0].append(p[1])
    for i in p[2]:
        p[0].append(i)
    p[0].append(p[3])

def p_num(p):
    '''
    num : NUMI
        | NUMF
        | ID
    '''
    p[0]=p[1]

def p_num_neg(p):
    '''
    num : '-' NUMI
        | '-' NUMF
        | '-' ID
    '''
    p[0]=p[1]

def p_arit(p):
    '''
    arit : '+'
        | '-'
        | '*'
        | '/'
        | '^'
    '''
    p[0]=p[1]

def p_boolexpr_bin(p):
    '''
    boolexpr : boolexpr AND boolexpr
        | boolexpr OR boolexpr
        | boolexpr EQUALS boolexpr
        | boolexpr NOTEQUALS boolexpr
    '''
    p[0]=Node(p[2],[p[1],p[3]])
    setParentOfChildren(p[0])

def p_boolexpr_idnum(p):
    '''
    boolexpr : ID EQUALS numexpr
        | ID NOTEQUALS numexpr
        | ID GTREQTHAN numexpr
        | ID LSSEQTHAN numexpr
        | ID '<' numexpr
        | ID '>' numexpr
    '''
    p[0]=Node(p[2],[Node(p[1]),treeFromInfix(p[3])])
    setParentOfChildren(p[0])

def p_boolexpr_idbool(p):
    '''
    boolexpr : ID EQUALS boolexpr
        | ID NOTEQUALS boolexpr
    '''
    p[0]=Node(p[2],[Node(p[1]),p[3]])
    setParentOfChildren(p[0])

def p_boolexpr_one(p):
    '''
    boolexpr : boolop
    '''
    p[0]=p[1]

def p_boolexpr_par(p):
    '''
    boolexpr : '(' boolexpr ')'
    '''
    p[0]=p[2]

def p_boolop(p):
    '''
    boolop : numcomp
        | bool
    '''
    p[0]=p[1]

def p_bool(p):
    '''
    bool : TRUE
        | FALSE
        | ID
    '''
    p[0]=Node(p[1])

def p_numcomp(p):
    '''
    numcomp : numexpr comp numexpr
    '''
    p[0]=Node(p[2],[treeFromInfix(p[1]),treeFromInfix(p[3])])
    setParentOfChildren(p[0])

def p_comp(p):
    '''
    comp : EQUALS
        | NOTEQUALS
        | GTREQTHAN
        | LSSEQTHAN
        | '<'
        | '>'
    '''
    p[0]=p[1]

def p_print(p):
    '''
    stmtprint : PRINT '(' expr ')'
    '''
    p[0]=Node(p[1],[p[3]])
    setParentOfChildren(p[0])

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    print(p)
    sys.exit('\033[91m' + "[ ! ] Error sintáctico" + '\033[0m')
    pass

#Se crea el parser
parser = yacc.yacc()

root=parser.parse(lexer=lexer.lexer, input=open("code2.txt").read())
if root == None:
    sys.exit('\033[91m' + "[ ! ] Error sintáctico" + '\033[0m')

def printChildren(node,level=0):
    print((' '*level)+node.type)
    if node.children:
        for i in node.children:
            printChildren(i, level+1)

printChildren(root)

