from parser import Node, printChildren
import sys
from semantics import semanticAnalysis, setVariables, root, variables, getVarType

tNodes = {}
lNodes = {}

tCounter = 1
lCounter = 1

f = open("output.txt","w")

def generateTAC(node):
    global tCounter
    global lCounter
    global f
    if node.type in ["block", "else"]:
        for child in node.children:
            generateTAC(child)
    elif node.type == "declaration":
        varType = node.children[1].type
        f.write(varType + "decl("+node.children[0].type+")\n")
        tNodes[node]=node.children[0].type
    elif node.type == "assignment":
        generateTAC(node.children[0])
        generateTAC(node.children[1])
        f.write(tNodes[node.children[0]]+":="+tNodes[node.children[1]]+"\n")
    elif node.type in ["int2float","int2string","float2string"]:
        generateTAC(node.children[0])
        f.write("t"+str(tCounter)+" := "+node.type+"("+tNodes[node.children[0]]+")"+"\n")
        tNodes[node]="i"+str(tCounter)
        tCounter+=3
    elif node.type in ["+","-","/","*","^","concat"]:
        generateTAC(node.children[0])
        generateTAC(node.children[1])
        f.write("t"+str(tCounter)+" := "+tNodes[node.children[0]]+ " "+node.type+" "+tNodes[node.children[1]]+"\n")
        tNodes[node]="t"+str(tCounter)
        tCounter+=1
    elif node.type in ["!=","==","<",">","<=",">="]:
        generateTAC(node.children[0])
        generateTAC(node.children[1])
        f.write("if ("+tNodes[node.children[0]]+" "+node.type+" "+tNodes[node.children[1]]+") goto L"+str(lCounter)+"\n")
        f.write("t"+str(tCounter)+" := false"+"\n")
        f.write("goto L"+str(lCounter+1)+"\n")
        f.write("\nL"+str(lCounter)+"\n")
        f.write("t"+str(tCounter)+" := true"+"\n")
        f.write("\nL"+str(lCounter+1)+"\n")
        tNodes[node]="t"+str(tCounter)
        tCounter+=1
        lCounter+=2
    elif node.type == "and":
        generateTAC(node.children[0])
        generateTAC(node.children[1])
        f.write("if ("+tNodes[node.children[0]]+") goto L"+str(lCounter)+"\n")
        f.write("t"+str(tCounter)+" := false"+"\n")
        f.write("goto L"+str(lCounter+2)+"\n")
        f.write("\nL"+str(lCounter)+"\n")
        f.write("if ("+tNodes[node.children[1]]+") goto L"+str(lCounter+1)+"\n")
        f.write("t"+str(tCounter)+" := false"+"\n")
        f.write("goto L"+str(lCounter+2)+"\n")
        f.write("\nL"+str(lCounter+1)+"\n")
        f.write("t"+str(tCounter)+" := true"+"\n")
        f.write("\nL"+str(lCounter+2)+"\n")
        tNodes[node]="t"+str(tCounter)
        tCounter+=1
        lCounter+=3
    elif node.type == "or":
        generateTAC(node.children[0])
        generateTAC(node.children[1])
        f.write("if ("+tNodes[node.children[0]]+") goto L"+str(lCounter)+"\n")
        f.write("if ("+tNodes[node.children[1]]+") goto L"+str(lCounter)+"\n")
        f.write("t"+str(tCounter)+" := false"+"\n")
        f.write("goto L"+str(lCounter+1)+"\n")
        f.write("\nL"+str(lCounter)+"\n")
        f.write("t"+str(tCounter)+" := true"+"\n")
        f.write("\nL"+str(lCounter+1)+"\n")
        tNodes[node]="t"+str(tCounter)
        tCounter+=1
        lCounter+=2
    elif node.type in ["if","elif"]:
        generateTAC(node.children[0])
        f.write("if ("+tNodes[node.children[0]]+") goto L"+str(lCounter)+"\n")
        f.write("goto L"+str(lCounter+1)+"\n")
        f.write("\nL"+str(lCounter)+"\n")
        saveLCount = lCounter
        lCounter+=2
        generateTAC(node.children[1])
        saveLCount2=lCounter
        if node.type == "if":
            f.write("goto L"+str(lCounter)+"\n")
            lNodes[node] = str(lCounter)
            lCounter+=1
        else:
            lNodes[node]=lNodes[node.parent]
            f.write("goto L"+lNodes[node.parent]+"\n")
        f.write("\nL"+str(saveLCount+1)+"\n")
        if(len(node.children)>2):
            generateTAC(node.children[2])
        if(len(node.children)>3):
            generateTAC(node.children[3])
        if node.type == "if":
            f.write("\nL"+str(saveLCount2)+"\n")
    elif node.type == "while":
        generateTAC(node.children[0])
        f.write("\nL"+str(lCounter)+"\n")
        f.write("if ("+tNodes[node.children[0]]+") goto L"+str(lCounter+1)+"\n")
        f.write("goto L"+str(lCounter+2)+"\n")
        f.write("\nL"+str(lCounter+1)+"\n")
        saveLCount=lCounter
        lCounter+=3
        generateTAC(node.children[1])
        f.write("goto L"+str(saveLCount)+"\n")
        f.write("\nL"+str(saveLCount+2)+"\n")
    elif node.type == "dowh":
        f.write("\nL"+str(lCounter)+"\n")
        saveLCount=lCounter
        lCounter+=1
        generateTAC(node.children[0])
        generateTAC(node.children[1])
        f.write("if ("+tNodes[node.children[1]]+") goto L"+str(saveLCount)+"\n")
    elif node.type == "for":
        generateTAC(node.children[0])
        f.write("\nL"+str(lCounter)+"\n")
        saveLCount=lCounter
        lCounter+=1
        generateTAC(node.children[1])
        f.write("\nL"+str(lCounter)+"\n")
        f.write("if ("+tNodes[node.children[1]]+") goto L"+str(lCounter+1)+"\n")
        f.write("goto L"+str(lCounter+2)+"\n")
        f.write("\nL"+str(lCounter+1)+"\n")
        saveLCount2=lCounter
        lCounter+=3
        generateTAC(node.children[3])
        generateTAC(node.children[2])
        f.write("goto L"+str(saveLCount)+"\n")
        f.write("\nL"+str(saveLCount+2)+"\n")
    elif not node.children:
        if node.type[0] == "-":
            f.write("t"+str(tCounter)+" := 0 - "+node.type[1:]+"\n")
            tNodes[node]="t"+str(tCounter)
            tCounter+=1
        else:
            tNodes[node]=node.type



#printChildren(root)
generateTAC(root)
print('\033[92m' + "La compilacion fue exitosa. El resultado de 3AC es en output.txt" + '\033[0m')
