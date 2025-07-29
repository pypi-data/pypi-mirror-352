

from staq.stack import Stack, StackFrame, StackCell 
from staq.function import Function, FunctionArgument
from staq.archs.architecture import Architecture, Register
from typing import List
from cliify import commandParser, command
from cliify.splitHelper import splitWithEscapes

import re

@commandParser
class Arm32(Architecture):
    def __init__(self, session = None, stack = None):
        super().__init__('arm', session=session, stack=stack)
        self.endian = 'little'



        self.registers = {
            'r0': Register('r0', 4, 'Return Value'),
            'r1': Register('r1', 4, 'Arg 1'),
            'r2': Register('r2', 4, 'Arg 2'),
            'r3': Register('r3', 4, 'Arg 3'),
            'r4': Register('r4', 4, 'Arg 4'),
            'r5': Register('r5', 4, 'Arg 5'),
            'r6': Register('r6', 4, 'Arg 6'),
            'sp': Register('sp', 4, 'Stack Pointer'),
            'fp': Register('fp', 4, 'Base Pointer'),
            'lr': Register('lr', 4, 'Link Register'),
            'pc': Register('pc', 4, 'Program Counter')
        }
        self.setReg('sp', hex(self.stack.pointer))
        self.setReg('pc', '???')
        self.setReg('fp', hex(self.stack.baseAddress))
        self.setReg('lr', '???')

    def clear(self):

        for key in self.registers:
            self.registers[key].value = None
        
        self.setReg('sp', hex(self.stack.pointer))
        self.setReg('pc', '???')
        self.setReg('fp', hex(self.stack.baseAddress))
        self.setReg('lr', '???')



    def setInstructionPointer(self, val):
        self.setReg("pc", val)

    def setFramePointer(self, val):
        return super().setFramePointer(val)
    
    def setReturnValue(self, val):
        self.setReg("r0", val)

    def updateRegs(self):
        self.setReg('sp', self.stack.pointer)

    
    
    


    @command(completions={'function': lambda self: self.session.functions.keys()})
    def call(self, function):
        """
        ARM32 implementation of the call command. Handles function calls according to ARM32 calling convention.
        Arguments are placed in r0-r3 registers first, with any additional arguments pushed onto the stack.
        """

        callLine = function.strip()
        regex = re.compile(r"(\S.*?)\((.*?)\)")
        match = regex.match(callLine)
        
        func = None
        
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
            args = splitWithEscapes(argStr, ',')
        
        # If the function does not exist, create it and assume all args are ints
        if functionName not in self.session.functions:
            newFunction = Function(functionName)
            
            for i in range(len(args)):
                newFunction.addArgument(FunctionArgument('int', f'arg{i+1}'))
            
            self.session.functions[functionName] = newFunction
        
        func = self.session.functions[functionName]
        
        # Save caller's lr register to keep track of return address
        self.setReg('lr', '<return_address>')
        
        # Handle arguments according to ARM32 calling convention
        # First 4 args go in r0-r3, rest on stack
        for i in range(len(args)):
            arg_value = args[i].strip()
            arg_label = f'arg{i+1}'
            
            # Use the argument name if available
            if i < len(func.args) and func.args[i].name:
                arg_label = func.args[i].name
            
            if i < 4:
                # First 4 args go in r0-r3
                self.setReg(f'r{i}', arg_value, note=arg_label)
            else:
                # Push remaining args on stack (in reverse order per ARM convention)
                # For ARM, we need to adjust the stack pointer
                cell = StackCell(arg_label, [arg_value])
                self.stack.push(cell)
        
        # Set up the return address on the stack
        currentFunction = self.session.getCurrentFunction()
        
        retCell = StackCell('ret', ['<???>'])
        if currentFunction:
            if isinstance(currentFunction, Function):
                retCell.setWords(f'<{currentFunction.name}+??>')
            else:
                retCell.setWords(f'<{currentFunction}+??>')
        
        self.stack.push(retCell)
        
        # Jump to the function (in ARM this would be a BL instruction)
        self.jmp(functionName)
        
        # Allocate local variables for the function
        if func:
            for local in func.locals:
                cell = self.session.tryParseLocalVar(local)
                if cell:
                    self.stack.push(cell)