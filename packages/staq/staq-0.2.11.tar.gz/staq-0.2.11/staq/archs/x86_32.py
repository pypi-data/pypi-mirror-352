

from staq.stack import Stack, StackFrame, StackCell 
from staq.function import Function, FunctionArgument
from staq.archs.architecture import Architecture, Register
from typing import List
from cliify import commandParser, command
from cliify.splitHelper import splitWithEscapes

import re

@commandParser
class X86_32(Architecture):
    def __init__(self, session = None, stack = None):
        super().__init__('x86_32', session=session, stack=stack)
        self.endian = 'little'


        self.registers = {
            'eax': Register('eax', 4, 'Return Value'),
            'ecx': Register('ecx', 4, 'Arg 1'),
            'edx': Register('edx', 4, 'Arg 2'),
            'ebx': Register('ebx', 4, 'Arg 3'),
            'esp': Register('esp', 4, 'Stack Pointer'),
            'ebp': Register('ebp', 4, 'Base Pointer'),
            'esi': Register('esi', 4, 'Source Index'),
            'edi': Register('edi', 4, 'Destination Index'),
            'eip': Register('eip', 4, 'Instruction Pointer')
        }

        self.setReg('esp', hex(self.stack.pointer))
        self.setReg('eip', '???')
        self.setReg('ebp', hex(self.stack.baseAddress))

    def clear(self):

        for key in self.registers:
            self.registers[key].value = None
        
        self.setReg('esp', hex(self.stack.pointer))
        self.setReg('eip', '???')
        self.setReg('ebp', hex(self.stack.baseAddress))



    def setInstructionPointer(self, val):

        self.setReg("eip", val)

    def setFramePointer(self, val):
        self.setReg("ebp", val)

    def setReturnValue(self, val):
        self.setReg("eax", val)
    
    @command
    def leave(self):


        if self.stack.currentFrame:
            while self.stack.pointer < self.registers['ebp'].value:
                self.stack.pop()
        
        self.pop('ebp')
    
    @command(completions={'function': lambda self: self.session.functions.keys()})
    def call(self, function):

        callLine = function.strip()

        regex = re.compile(r"(\S.*?)\((.*?)\)")

        match = regex.match(callLine)

        func : Function = None

        if match:

            functionName = match.group(1)

            args = match.group(2)

        else:
            functionName = callLine
            args = ""

        if args.strip() == "":
            args = []
        else:
            argStr = match.group(2)
            args = splitWithEscapes(argStr,',')


        # If the function does not exist, create it and assume all args are ints
        if functionName not in self.session.functions:
            newFunction = Function(functionName)

            for i in range(len(args)):
                newFunction.addArgument(FunctionArgument('int',f'arg{i+1}'))

            self.session.functions[functionName] = newFunction

        func  = self.session.functions[functionName]
        
        for i in reversed(range(len(args))):
            label = f'arg{i+1}'
            if i < len(func.args) and func.args[i].name: 
                label = f"{func.args[i].name}"
            

            cell = StackCell(  label, [args[i].strip()])
            self.stack.push(cell)

        currentFunction = self.session.getCurrentFunction()

        
        retCell = StackCell('ret', ['<???>'])
        if currentFunction:

            if isinstance(currentFunction, Function):
                
                retCell.setWords(f'<{currentFunction.name}+??>')
            else:
                retCell.setWords(f'<{currentFunction}+??>')

        self.stack.push(retCell)

        self.jmp(functionName)

        ebpCell = StackCell('prev ebp', [self.registers['ebp'].value])
        self.stack.push(ebpCell)
        self.registers['ebp'].value = self.stack.pointer
        
        
        if func:
            for local in func.locals:
                cell = self.session.tryParseLocalVar(local)
                if cell:
                    self.stack.push(cell)



        