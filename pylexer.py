import ply.lex as lex

#Literales
literals = ['=', '+', '-', '*', '/', '^', '(', ')', '{', '}', '<', '>', ';']

#Palabras reservadas del analisis sintactico
reserved = {
    'and' : 'AND',
    'or' : 'OR',
    'if' : 'IF',
    'elif' : 'ELIF',
    'else' : 'ELSE',
    'boolean' : 'BOOLEAN',
    'float' : 'FLOAT',
    'int' : 'INT',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'print' : 'PRINT',
}

#Palabras reservadas para los tokens
tokens = [
    'NUMI', 'NUMF', 'ID', "EQUALS", "NOTEQUALS", "GTREQTHAN", "LSSEQTHAN"
] + list(reserved.values())

#Tokens (Se usan expresiones regulares para reconocerlos)
t_EQUALS = r'=='
t_NOTEQUALS = r'!='
t_GTREQTHAN = r'>='
t_LSSEQTHAN = r'<='
t_NUMI = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'
t_NUMF = r'((\d+)(\.\d+)(e(\+|-)?(\d))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'
t_ignore = ' \t'

#Nos ayuda a reconocer el salto de linea
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value) #Devuelve el número de línea acumulativo de la línea que se acaba de leer

#Nos ayuda a reconocer los IDs
def t_ID(t):
    r'[A-Za-z_][\w_]*'
    t.type = reserved.get(t.value, "ID")
    return t

#Nos ayuda a reconocer el error
def t_error(t):
    print("Caracter ilegal %s", repr(t.value[0]))
    t.lexer.skip(1)

#Construir el lexer
lexer = lex.lex()