import random
from string import ascii_lowercase, ascii_letters
from itertools import repeat, product

def generate(Nvar, Nops):
    possible = ['(I&F)', '(I|F)', '(I->F)', '(F->I)', '(I<->F)']
    stmt = random.choice(possible)
    while stmt.count('F') < Nops:
        idx = random.choice([i for i, ele in enumerate(stmt) if ele == 'I'])
        stmt = stmt[:idx] + random.choice(possible) + stmt[idx+1:]
    stmt = stmt.replace('I', 'F')
    variables = random.sample(ascii_lowercase, Nvar)
    Fs = [i for i, ele in enumerate(stmt) if ele == 'F']
    for i in range(random.randint(0, len(Fs))):
        Fs = [i for i, ele in enumerate(stmt) if ele == 'F']
        var = random.choice(Fs)
        stmt = stmt[:var] + '(¬F)' + stmt[var+1:]
    for idx, var in enumerate([i for i, ele in enumerate(stmt) if ele == 'F']):
        stmt = stmt[:var] + variables[idx%Nvar] + stmt[var+1:]
    return stmt


class BoolExpr:
    def __init__(self, s):
        self.s = s
        self.parsed = []
        self.postfix = []
        self.__parse()
        assert self.__validate()
        self.__in2post()
        
    def __validate(self):
        for i in self.parsed:
            if i not in ''.join(list(TTGen.operators.keys()))+ascii_letters+'()':
                return False
        return True
        
    def __parse(self):
        i = 0
        n = len(self.s)
        while i < n:
            for op in TTGen.operators.keys():
                if len(op) > 1 and n - i >= len(op) and all([self.s[i+idx] == c for idx, c in enumerate(op)]):
                    self.parsed.append(op)
                    i += len(op)
                    break
            else:
                self.parsed.append(self.s[i])
                i += 1
    
    def __in2post(self):
        i = 0
        n = len(self.parsed)
        stack = []
        while i < n:
            char = self.parsed[i]
            if char == ')':
                while stack[-1] != '(':
                    self.postfix.append(stack.pop())
                stack.pop()
            elif char in list(TTGen.operators.keys()) or char == '(':
                stack.append(char)
            elif char != '(':
                self.postfix.append(char)
            i += 1
        if stack: self.postfix.append(stack[-1])

class Node:
    def __init__(self, value, op=True):
        self.left = None
        self.right = None
        self.value = value
        self.op = op
        self.terminal = not op
        
    def traverse(self):
        if self.left:
            self.left.traverse()
        print(self.value, end='')
        if self.right:
            self.right.traverse()
        
    
    def __repr__(self):
        return f'Node({self.value}, op={self.op})'
    
    def evaluate(self, inputs):
        if self.terminal:
            idx = inputs[0].index(self.value)
            return inputs[1][idx]
        if self.left:
            left = self.left.evaluate(inputs)
        if self.right:
            right = self.right.evaluate(inputs)
        if self.op and self.left and self.right:
            op = self.value
            return TTGen.operators[op](left, right)
        if self.op and self.left:
            op = self.value
            return TTGen.operators[op](left)
                    

class TTGen:
    operators = {
        "|": lambda x, y: x or y,
        "¬": lambda x: not x,
        "&": lambda x, y: x and y,
        "->": lambda x, y: True if not x or (x and y) else False,
        "<->": lambda x, y: True if x == y else False,
    }
    
    def __init__(self, stmt):
        self.stmt = stmt
        self.postfix = BoolExpr(stmt).postfix
        self.tree = self.buildTree()
        
    def buildTree(self):
        stack = []
        for char in self.postfix:
            if char in list(TTGen.operators.keys()):
                if char == '¬':
                    x = stack.pop()
                    node = Node(char, True)
                    node.left = x
                    stack.append(node)
                else:
                    y = stack.pop()
                    x = stack.pop()
                    node = Node(char, True)
                    node.left = x
                    node.right = y
                    stack.append(node)
                continue
            else:
                stack.append(Node(char, False))
        return stack[0]
    
    def getVariables(self):
        self.variables = []
        for i in self.postfix:
            if i in self.variables or i in list(TTGen.operators.keys()):
                continue
            self.variables.append(i)
        self.variables.sort()
    
    def genTT(self):
        self.getVariables()
        
        n = len(self.variables)
        inputCombinations = product((False, True), repeat=n)
        results = {'T':0, 'F':0}
        print(' '.join(self.variables) + ' out')
        for inputs in zip(repeat(self.variables, 2**n), inputCombinations):
            result = 'T' if self.tree.evaluate(inputs) else 'F'
            print(' '.join(['T' if i else 'F' for i in inputs[1]]) + f'  {result} ')
            results[result] += 1
        print(results)
  
filename = 'truthtable.csv'
        
stmt = generate(5, 20)
print(stmt)
expr = TTGen(stmt)
expr.genTT()
        