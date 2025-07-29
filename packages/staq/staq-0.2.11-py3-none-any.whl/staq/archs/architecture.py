
from staq.stack import Stack, StackFrame, StackCell 
from staq.function import Function, FunctionArgument
from termcolor import colored
from cliify import commandParser, command
from cliify.splitHelper import splitWithEscapes

import re
import json
import yaml



sizeDict = {
    "void": 0,
    "char": 1,
    "unsigned char": 1,
    "signed char": 1,
    "short": 2,
    "unsigned short": 2,
    "int": 4,
    "unsigned int": 4,
    "long": 4,
    "unsigned long": 4,
    "long long": 8,
    "unsigned long long": 8,
    "float": 4,
    "double": 8,
    "long double": 16,  # This can vary, but 16 bytes is a common size
    "int8": 1,
    "uint8": 1,
    "int16": 2,
    "uint16": 2,
    "int32": 4,
    "uint32": 4,
    "int64": 8,
    "uint64": 8,
    "va_list": 4,
}


class Register():
    def __init__(self, name, size, description):
        self.name = name
        self.size = size
        self.type = type
        self.value = None
        self.description = None
        self.note = None


@commandParser
class Architecture():
    """
        Base Class for calling conventions
    """
    def __init__(self, name, session = None, stack = None):
        self.name = name
        self.endian = 'little'
        self.registers = {}
        self.session = session
        self.stack : Stack = stack
        self.wordSize = 4

    def clear(self):

        for key in self.registers:
            self.registers[key].value = None


    def setInstructionPointer(self, val):
        pass

    def setFramePointer(self, val):
        pass

    def setReturnValue(self, val):
        pass

    @command(completions={'arg': ['frame']})
    def pop(self, arg: str = None):
        """
            Pop a value from the stack
            
            pop frame
            pop eax
            pop {eax,ebx,ecx}
            pop { r0-r3, r5}
        """
        if arg == 'frame':
            return self.popFrame()
        elif arg is None:
            self.stack.pop()
        elif arg in self.registers:
            self.setReg(arg, self.stack.pop())
        elif arg.startswith('{') and arg.endswith('}'):
            arg = arg.replace('{','[').replace('}',']')
            parsed = yaml.load(arg, Loader=yaml.FullLoader)
            for x in parsed:
                if x in self.registers:
                    self.setReg(x, self.stack.pop())
                elif '-' in x:
                    start_end = x.split('-')
                    if len(start_end) == 2:
                        start = start_end[0].strip()
                        end = start_end[1].strip()
                        if start in self.registers and end in self.registers:
                            startIndex = list(self.registers.keys()).index(start)
                            endIndex = list(self.registers.keys()).index(end)
                            for i in range(startIndex, endIndex + 1):
                                regName = list(self.registers.keys())[i]
                                self.setReg(regName, self.stack.pop())
        elif arg.isnumeric():
            self.stack.pop(int(arg))

    @command(completions={'arg': ['frame']})
    def push(self, arg: str = None, label: str = None, note: str = None, size: int = 0):
        """
            Push a value to the stack

            push frame
            push eax
            push r0 
            push {eax,ebx,ecx}
            push { r0-r3, r5}
        """


        cell = StackCell(label=label)

        if arg == 'frame':
            return self.pushFrame()
        elif arg in self.registers:
            cell.setWords(self.getReg(arg))
            cell.words[0].note = note
            self.stack.push(cell)
        elif arg and arg.startswith('{') and arg.endswith('}'):
            arg = arg.replace('{','[').replace('}',']')
            parsed = yaml.load(arg, Loader=yaml.FullLoader)
            for x in parsed:
                cell = StackCell(label=label)
                if x in self.registers:
                    cell.setWords(self.getReg(x))
                    cell.words[0].note = note
                    self.stack.push(cell)
                elif '-' in x:
                    start_end = x.split('-')
                    if len(start_end) == 2:
                        start = start_end[0].strip()
                        end = start_end[1].strip()
                        if start in self.registers and end in self.registers:
                            startIndex = list(self.registers.keys()).index(start)
                            endIndex = list(self.registers.keys()).index(end)
                            for i in range(startIndex, endIndex + 1):
                                cell = StackCell(label=label)
                                regName = list(self.registers.keys())[i]
                                cell.setWords(self.getReg(regName))
                                cell.words[0].note = note
                                self.stack.push(cell)

        else:
            #try to parse the arg as a number
            try:
                cell.setWords(arg)
                if size > 0:
                    cell.setSize(size)
                cell.words[0].note = note
                self.stack.push(cell)
            except ValueError:
                pass

    @command
    def local(self, line: str,note: str = None):
        """
            Add a local variable to the stack using line

            int singleInt = 4
            int array[10] = {0,1,2,3,4,5,6,7,8,9}
            int *ptr
            char *ptr[10]
            float* ptr[10]
        """

        cell = StackCell(note=note)

        #split the line into parts
        left_right = splitWithEscapes(line, '=')

        if len(left_right) == 1:
            left = left_right[0]
            right = ""
        elif len(left_right) == 2:
            left = left_right[0]
            right = left_right[1]

        left = left.strip()
        right = right.strip()
        elSizeBytes = 4
        elCount = 1
        if right != "":
            right = right.replace('{','[').replace('}',']')
            if right.startswith('[') and right.endswith(']'):
                parsed = yaml.safe_load(right)
                if isinstance(parsed, list):
                    elCount = len(parsed)
            
                cell.setWords(parsed)
            else:
                cell.setWords(right)
        
        leftParts = splitWithEscapes(left, ' ')
        if len(leftParts) == 2:
            type = leftParts[0]
            name = leftParts[1]
            isPointer = False
            if name.startswith('*'):
                isPointer = True
                name = name[1:]
                elSizeBytes = 4
            
            if type.endswith('*'):
                isPointer = True
                type = type[:-1]
                elSizeBytes = 4
            
            if not isPointer:
                if type in sizeDict:
                    elSizeBytes = sizeDict[type]
                else:
                    raise ValueError(f"Unknown type: {type}")

            regex = re.compile(r"(\S+)\[(\d+)\]")
            match = regex.match(name)
            if match:
                name = match.group(1)
                declaredSize = int(match.group(2))
                if declaredSize > elCount:
                    elCount = declaredSize
        
        cell.setSize(elSizeBytes * elCount / self.wordSize)
        cell.label = name

        self.stack.push(cell)
                
    @command
    def int(self, line, note: str = None):
        self.local("int " + line, note)
    
    @command
    def char(self, line, note: str = None):
        self.local("char " + line, note)
    @command
    def short(self, line, note: str = None):
        self.local("short " + line, note)
    @command
    def long(self, line, note: str = None):
        self.local("long " + line, note)
    @command
    def float(self, line, note: str = None):
        self.local("float " + line, note)
    @command
    def double(self, line, note: str = None):
        self.local("double " + line, note)


    
    def popFrame(self):
       return self.stack.popFrame()
    
    def pushFrame(self, frame):
        self.stack.pushFrame(frame)

    def getReg(self, key):
        if key in self.registers:
            return self.registers[key].value
        
        return None
    
    def setReg(self,key, value, note = None, create=True):

        if key in self.registers:
            self.registers[key].value = value
            self.registers[key].note = note
        else:
            if create:
                self.registers[key] = Register(key, 4, note)
                self.registers[key].value = value
                self.registers[key].note = note
            else:
                raise ValueError(f"Register {key} not found")

    @command
    def leave(self):

        if self.stack.currentFrame:
            while self.stack.currentFrame.length() > 1:
                self.stack.pop()
            
            while self.stack.currentFrame.cells[0].size > 1:
                self.stack.pop()

    @command
    def ret(self, value = None):
        """
            Return from the current function
        """
        word = self.stack.pop()

        if value:
            self.setReturnValue(value)


        if word and word.value:
            self.jmp( word.value)
        else:
            self.jmp('???')

    def markArgs(self): 

        self.stack.argMarks = {}

        if self.stack.currentFrame and self.stack.currentFrame.function:
            func = self.stack.currentFrame.function

            pointer = self.stack.currentFrame.basePointer
            pointer+= 1 #skip the return address
            for i in range(len(func.args)):
                
                self.stack.argMarks[pointer] = func.args[i].name
                pointer += func.args[i].size


    @command
    def jmp(self, address):

        val = address
        self.setInstructionPointer(val)

        offset = 0

        if val.startswith('<') and val.endswith('>'):
            val = val[1:-1]

        val = val.strip()

        if '+' in val:
            
            val, offset = val.split('+')


        if self.stack.currentFrame and self.stack.currentFrame.function and self.stack.currentFrame.function.name == val:
            pass 
        else:
            lastWord = self.stack.pop()
            func = self.session.functions.get(val, Function(val))
            self.stack.pushFrame(StackFrame(val,func))
            cell = StackCell('ret', [lastWord])

            self.stack.push(cell)

        self.markArgs()

    def updateRegs(self):
        self.setReg('esp', self.stack.pointer)


    def registersToAnsi(self, width = 30, color='yellow'):

        #  ┌───────────────────────────────────┐
        #  │ esp: <value>                      │
        #  │ ebp: <value>                      │
        #  │ eax: <value>                      │
        #  │ ebx: <value>                      │
        #  └───────────────────────────────────┘

        self.updateRegs()

        #get the max length of the register names
        maxNameLength = 0
        for key in self.registers:
            if len(key) > maxNameLength:
                maxNameLength = len(key)
        
        maxValLength =  width - (maxNameLength + 5)

        out = colored(f"┌{'─' * maxNameLength}{'─' * (maxValLength +5)}┐\n", color)
        for key in self.registers:
            if self.registers[key].value:

                if isinstance(self.registers[key].value, int):
                    strVal = hex(self.registers[key].value)
                else:
                    strVal = str(self.registers[key].value)

                truncVal = strVal.ljust(maxValLength)[:maxValLength]
                out += colored(f"│ {key.rjust(maxNameLength)} : {truncVal} │\n", color)

        out += colored(f"└{'─' * maxNameLength}{'─' * (maxValLength + 5)}┘\n", color)

        return out

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

        if func:
            for local in func.locals:
                cell = self.session.tryParseLocalVar(local)
                if cell:
                    self.stack.push(cell)


        

    