from pyparser import Node, root, printChildren
import pyparser
import sys
import re
import copy

class VariablePLY:
    def __init__(self,value,typ):
        self.typ=typ
        self.value=value

variables={ }

def getVarType(node, varName):
    if node in variables.keys() and varName in (o.value for o in variables[node]):
        return [x for x in variables[node] if x.value == varName][0].typ
    if node.type == "else" or node.type == "elif":
        currentNode = node.parent
        while((currentNode.type == "if" or currentNode.type == "elif") and currentNode.parent):
            currentNode = currentNode.parent
        return getVarType(currentNode, varName)
    if node.parent:
        return getVarType(node.parent, varName)
    else:
        return None

def findScopeNode(node):
    if(node.type in ["block", "for", "dowh", "if", "elif", "else", "while"]):
        return node
    if(node.parent):
        return findScopeNode(node.parent)
    return Node('Self')

def isVarInTree(node,varName):
    if node.children:
        for child in node.children:
            isVarInTree(child,varName)
    elif node.type==varName:
        sys.exit('\033[91m' + "[ ! ] Asignación inválida" + '\033[0m')

def printVariables(r):
    if r.type=="declaration":
        print(r.children[0].type+" declarado como "+r.children[1].type+ " dentro de "+findScopeNode(r).type)
        scopeNode = findScopeNode(r)
        if scopeNode in variables.keys():
            variables[scopeNode].append(VariablePLY(r.children[0].type,r.children[1].type))
        else:
            variables[scopeNode]=[VariablePLY(r.children[0].type,r.children[1].type)]
    if r.children:
        for child in r.children:
            printVariables(child)

def isWithinScope(node, varName):
    if node in variables.keys() and varName in (o.value for o in variables[node]):
        return True
    if node.type=="else" or node.type=="elif":
        currentNode=node.parent
        while((currentNode.type=="if" or currentNode.type=="elif")):
            currentNode = currentNode.parent
            if currentNode == None:
                return False
        return isWithinScope(currentNode, varName)
    if node.parent:
        return isWithinScope(node.parent,varName)
    else:
        return False

def treeNumTypeCheck(node):
    if node.children:
        if not node.type in ["+","-","/","*","^"]:
            sys.exit('\033[91m' + "[ ! ] Asignación de número inválida " + '\033[0m')
        for child in node.children:
            treeNumTypeCheck(child)
        if node.children[0].ptype == node.children[1].ptype:
            node.ptype=node.children[0].ptype
        else:
            for i in range(len(node.children)):
                if node.children[i].ptype=="int":
                    parseNode=Node('int2float',ptype="float")
                    node.children[i].parent=parseNode
                    parseNode.children[i]=[node.children[i]]
                    node.children[i]=parseNode
            node.ptype="float"
    else:
        if(re.fullmatch(r'-?\d+([uU]|[lL]|[uU][lL]|[lL][uU])?',node.type)):
            node.ptype="int"
        elif(re.fullmatch(r'-?((\d+)(\.\d+)(e(\+|-)?(\d))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?', node.type)):
            node.ptype="float"
        else:
            if((node.type[0]=="-" and not isWithinScope(node,node.type[1:])) or (node.type[0] != "-" and not isWithinScope(node,node.type))):
                sys.exit('\033[91m' + "[ ! ] La variable " + node.type + " no está declarada en el scope." + '\033[0m')
            if(node.type[0]=="-"):
                varType=getVarType(node,node.type[1:])
            else:
                varType=getVarType(node,node.type)
            if varType=="string" or varType=="boolean":
                sys.exit('\033[91m' + "[ ! ] No se puede convertir " + varType + " a numero." + '\033[0m')
            node.ptype=varType
    #print(node.type+" is "+node.ptype)


def treeStrTypeCheck(node):
    if node.type == "num2string":
        treeNumTypeCheck(node.children[0])
        node.type=node.children[0].ptype + "2string"
        node.ptype="String"
    elif not node.children:
        if not re.fullmatch(r'\"([^\\\n]|(\\.))*?\"',node.type):
            if not re.fullmatch(r'[A-Za-z_][\w_]*',node.type):
                sys.exit('\033[91m' + "[ ! ] No se puede convertir " + node.type + " a string." + '\033[0m')
            if not isWithinScope(node, node.type):
                sys.exit('\033[91m' + "[ ! ] La variable " + node.type + " no está declarada en el scope." + '\033[0m')
            varType=getVarType(node,node.type)
            if varType != "string":
                sys.exit('\033[91m' + "[ ! ] No se puede convertir " + varType + " a string." + '\033[0m')
        node.ptype="string"
    else:
        if node.type != "concat":
            sys.exit('\033[91m' + "[ ! ] Asignación inválida de string" + '\033[0m')
        for child in node.children:
            treeStrTypeCheck(child)


def treeBoolTypeCheck(node):
    if not node.children:
        if node.type != "true" and node.type != "false":
            if not isWithinScope(node, node.type):
                sys.exit('\033[91m' + "[ ! ] La variable " + node.type + " no está declarada en el scope." + '\033[0m')
            varType=getVarType(node,node.type)
            if varType != "boolean":
                sys.exit('\033[91m' + "[ ! ] No se puede convertir " + varType + " a boolean." + '\033[0m')
    elif node.type in ["==","!="]:
        if(node.children[0].type in ["+","-","/","*","^"] or re.match(r'-?\d+([uU]|[lL]|[uU][lL]|[lL][uU])?', node.children[0].type)):
            treeNumTypeCheck(node.children[0])
            treeNumTypeCheck(node.children[1])
        elif(node.children[0].type in ["concat","num2string"] or re.fullmatch(r'\"([^\\\n]|(\\.))*?\"', node.children[0].type)):
            treeNumTypeCheck(node.children[0])
            treeNumTypeCheck(node.children[1])
        elif(node.children[0].type in ["==","!=","<",">",">=","<=","and","or","true","false"]):
            treeNumTypeCheck(node.children[0])
            treeNumTypeCheck(node.children[1])
        else:
            child0type=getVarType(node,node.children[0].type)
            if child0type == "float" or child0type == "int":
                treeNumTypeCheck(node.children[1])
            elif child0type == "string":
                treeStrTypeCheck(node.children[1])
            elif child0type == "boolean":
                treeBoolTypeCheck(node.children[1])
            else:
                sys.exit('\033[91m' + "[ ! ] La variable " + node.children[0].type + " ya está declarada en el scope." + '\033[0m')
    elif node.type in ["<",">","<=",">="]:
        treeNumTypeCheck(node.children[0])
        treeNumTypeCheck(node.children[1])
    elif node.type in ["and","or"]:
        treeBoolTypeCheck(node.children[0])
        treeBoolTypeCheck(node.children[1])

def setVariables(r):
    if(r.type == "declaration"):
        if isWithinScope(r,r.children[0].type):
            sys.exit('\033[91m' + "[ ! ] La variable" + r.children[0].type + " ya está declarada en el scope." + '\033[0m')
        #print(r.children[0].type + " declarado como " + r.children[1].type + " dentro de " + findScopeNode(r).type)
        scopeNode = findScopeNode(r)
        if scopeNode in variables.keys():
            variables[scopeNode].append(VariablePLY(r.children[0].type,r.children[1].type))
        else:
            variables[scopeNode]=[VariablePLY(r.children[0].type,r.children[1].type)]
    if r.children:
        for child in r.children:
            setVariables(child)


def semanticAnalysis(r):
    checkChildren = True

    if(r.type=="assignment"):
        correctType=""
        if r.children[0].type=="declaration":
            correctType = r.children[0].children[1].type
            varName = r.children[0].children[0].type
            isVarInTree(r.children[1], varName)
        elif (not isWithinScope(r,r.children[0].type)):
            sys.exit('\033[91m' + "[ ! ] La variable" + r.children[0].type + " no está declarada en el scope." + '\033[0m')
        else:
            correctType=getVarType(r,r.children[0].type)
        if correctType == "int" or correctType == "float":
            treeNumTypeCheck(r.children[1])
            if correctType == "float" and r.children[1].ptype == "int":
                parseNode=Node('int2float', ptype="float")
                r.children[1].parent=parseNode
                parseNode.children=[r.children[1]]
                r.children[1]=parseNode
            elif r.children[1].ptype != correctType:
                sys.exit('\033[91m' + "[ ! ] No se puede convertir" + r.children[1].ptype + " a " + correctType + "."+ '\033[0m')
        elif correctType == "string":
            treeStrTypeCheck(r.children[1])
        elif correctType == "boolean":
            treeBoolTypeCheck(r.children[1])
        checkChildren = False
    elif(r.type in ["+","-","/","*","^"] or re.match(r'-?\d+([uU]|[lL]|[uU][lL]|[lL][uU])?',r.type)):
        treeNumTypeCheck(r)
        checkChildren = False
    elif(r.type in ["concat","num2string"] or re.fullmatch(r'\"([^\\\n]|(\\.))*?\"',r.type)):
        treeStrTypeCheck(r)
        checkChildren = False
    elif(r.type in ["==","!=","<",">",">=","<=","and","or","true","false"]):
        treeBoolTypeCheck(r)
        checkChildren = False
    if r.children and checkChildren:
        for child in r.children:
            semanticAnalysis(child)

#printVariables(root)
setVariables(root)
semanticAnalysis(root)
#printChildren(root)
