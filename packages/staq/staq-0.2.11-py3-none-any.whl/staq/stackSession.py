
from staq.archs import X86_32, Arm32
from staq.stack import Stack, StackFrame, StackCell
from staq.function import Function, FunctionArgument, parseCFile
import re
import yaml
import json
import argparse
import re

from importlib.resources import files, as_file
import builtins
from cliify import command, commandParser
from cliify.splitHelper import splitWithEscapes


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


def nullPrint(*args, **kwargs):
    pass

builtins.print = nullPrint

@commandParser( subparsers=['arch'],flat=True)
class StackSession():
    def __init__(self, arch = None):
        self.stack = Stack()
        self.arch = None
        #self.arch = X86_cdecl(session=self, stack=self.stack)
        self.functions = {}
        self.parser = argparse.ArgumentParser(description='Stack Visualizer', add_help=False)
        self.subparsers = None
        self.loadLibcFuntions()
        self.commands = []
        self.update = False
        self.status = ""
        self.cmdIdx = 0

        if arch:
            self.setArch(arch)

    def setArch(self, arch):
        if arch == 'x86':
            self.arch = X86_32(session=self, stack=self.stack)
        elif arch == 'arm':
            self.arch = Arm32(session=self, stack=self.stack)
        else:
            self.arch = X86_32(session=self, stack=self.stack)

    def addHistory(self,cmd):

        if self.cmdIdx < len(self.commands):
            self.commands = self.commands[:self.cmdIdx]

        self.commands.append(cmd)
        self.cmdIdx+=1

    def stepForward(self):

        if self.cmdIdx < len(self.commands):
            self.parseCommand(self.commands[self.cmdIdx], addHistory=False)
            self.cmdIdx +=1

    def stepBack(self):

        if self.cmdIdx > 0:

            self.cmdIdx -= 1
            self.stack.clear()
            
            for i in range(0,self.cmdIdx):
                self.parseCommand(self.commands[i], addHistory=False)

    def print(self,text):
        print(text)

    def refreshOutput(self):

        ansi = self.stack.toAnsi( showAddress=True)
        print(ansi)

    def loadYaml(self, obj):


        if isinstance(obj, str):
            with open(obj) as f:
                obj = yaml.safe_load(f)


        order = 'normal'

        if 'stackBase' in obj:
            self.stack.baseAddress = obj['stackBase']
        
        if 'order' in obj:
            order = obj['order']

        if 'functions' in obj:
            for func in obj['functions']:
                self.addFunction(Function.fromString(func))
    

        if 'stack' in obj:

            nodes = []
            if order == 'normal':
                nodes = reversed(obj['stack'])
            else:
                nodes = obj['stack']

            for node in nodes:
                
               if isinstance(node, dict) and 'function' in node:
                   #Create a new frame 
                   frame = StackFrame.fromObj(node, order= order)
                   self.stack.pushFrame(frame)
                   self.stack.currentFrame = None
               else:
                    cell = StackCell.fromObj(node)
                    self.stack.push(cell)
        
        self.stack.applyAddresses()


    
    def getCurrentFunction(self):

        if self.stack.currentFrame:

            if self.stack.currentFrame.function:
                return self.stack.currentFrame.function
            
        
        return None

    def addFunction(self, function):
        self.functions[function.name] = function


    def loadLibcFuntions(self):
        
        data_path = files('staq.data').joinpath('libc.c')
        libc_functions = []
        with as_file(data_path) as f:
            with open(f) as libc_file:
                functions = parseCFile(libc_file.read())
                for func in functions:
                    self.addFunction(func)


   
    @command
    def frame(self, name, color = None):
        """
            frame <name> --color <color>
        """
        frame = StackFrame(name)
        if color:
            frame.color = color
        self.stack.pushFrame(frame)



    def parseFunction(self, line):

        function = Function.fromString(line)
        self.addFunction(function)


    # def functionCmd(self,args):
    #     line = " ".join(args.function)
    #     function = Function.fromString(line)
    #     self.addFunction(function)
    
    @command( completions={'file': ['$file']} )
    def save(self, file = None):

        filename = file




        if filename.endswith('.html'):
            with open(filename, "w") as f:
                f.write(self.stack.toHtml())

        elif filename.endswith('.png'):

            try:
                self.stack.generatePng(filename)
            except Exception as e:
                self.print("Failed to generate image. This is likely due to not having 'chrome' installed which is required for html2image. Please install chrome and try again.")

        else:
            with open(filename, "w") as f:
                for cmd in self.commands:
                    if not cmd.startswith("save"):
                        if not cmd.endswith("\n"):
                            cmd += "\n"
                        f.write(cmd)


                
        

    @command( completions={'file': ['$file']} )
    def load(self, file: str = None):
        filename = file
        self.update = False

        if filename.endswith('.c'):

            with open(filename) as f:
                functions = parseCFile(f.read())

            self.status = f"Loaded {len(functions)} functions from {filename}"

            for func in functions:
                self.addFunction(func)

    def getCellRefs(self) -> list:
        """
        Get a list of all cell references in the stack
        """
        cells = self.stack.getCells()
        refs = []

        for cell in cells:
            refs.append(f"&{cell.label}")

        return refs

    @command( completions={'file': ['$file'], 'data': lambda  self: self.getCellRefs(), 'address': lambda  self: self.getCellRefs(),  } )
    def write(self, data = None, address = None, file = None ):
        """
            write [data1,data2,data3] , address: &cell+4
            write &cell+16: [data1,data2,data3]
        
        """
        

        if file:
            #read file as bytes 
            with open(file, "rb") as f:
                data = f.read()
                data = list(data)


        if isinstance(data, str):
            if not data.startswith("[") and not data.endswith("]"):
                data = f"[{data}]"
            data = yaml.safe_load(data) #use yaml to parse the list so we get the correct types/escapes

        self.stack.write(data, address)

    @command( completions={'address': lambda  self: self.getCellRefs(), 'note': lambda  self: self.getCellRefs(), 'color': ['red', 'green', 'blue', 'yellow', 'purple'] } )
    def note(self, note = None, address = None, color = 'red'):
        """
            note 0x1234: note on local variable
            note 0x1234: note on local variable --color red
        """

        self.stack.setNote(note=note, address=address, color=color)

    @command(completions={'function': lambda self: self.functions.keys()})
    def run(self, function, limit = 20):

        called = True

        functionCall = None
        
        if function:
            function = function.strip()
            if function == "":
                function = None

        if function:
            functionCall = function
        elif self.stack.currentFrame and self.stack.currentFrame.function:
            function = self.stack.currentFrame.function

            if len(function.calls) > 0:
                functionCall  = function.calls[0]

        if not functionCall:
            functionCall = "main()"

        self.arch.call(functionCall)
        limit -= 1

        while  called and (limit > 0):
            
            if self.stack.currentFrame and self.stack.currentFrame.function: 
                function = self.stack.currentFrame.function

                if len(function.calls) > 0:
                    call = function.calls[0]
                    self.arch.call(call)
                    called = True

            limit -= 1


    @command
    def clear(self):
        self.stack.clear()


    def tryParseCommand(self, line, addHistory = True):
        """
        Try to parse a command. If it fails, try to parse with calling convention
        """
        plainCmd = line.split(" ")[0]

        if addHistory and plainCmd not in ['save','s', 'load','l']:
            self.addHistory(line)


        cmds = splitWithEscapes(line,";")

        for cmd in cmds:
            words = cmd.split(" ")
            firstWord = words[0]

            #If first word is a var declaration for a pointer, move the * to the beginning of the name 
            # i.e int* foo = 0x1234 becomes int *foo = 0x1234
            # This is to allow the command parser to work with the declaration
            if firstWord.endswith("*"):
                remaining = cmd[len(firstWord):].lstrip()
                firstWord = firstWord[:-1]
                cmd = firstWord + " *" + remaining
            
            if firstWord in ["write","note"]:
                """
                    if using shorthand for write, i.e. write &cell+16: [data1,data2,data3]
                """

                if (words[1].startswith("&") or words[1].startswith("0x")) and words[1].endswith(":"):
                    #write &cell+16: [data1,data2,data3]
                    cmd = f'{firstWord} {" ".join(words[2:])} , address: {words[1]}'
                    

            try:
                self.parseCommand(cmd.strip())
                self.refreshOutput()
            except Exception as e:
                pass





    def showHelp(self, command):
            
            if command in self.subparsers.choices:
                self.print(self.subparsers.choices[command].format_help() + "\n\n [Enter] to continue...")
            else:
                self.print(self.parser.format_help() + "\n\n [Enter] to continue...")

            #self.print("[Enterr] to continue...")

    def tryParseLocalVar(self, line):
        
        parts = line.split("=")

        
        revar = re.compile(r"(\w[\w\s\*]*\w)\s+(\w+)(\[(\d*)\])?")

        ptr = False

        decl = parts[0]
        if "*" in decl:
            ptr = True
            decl = decl.replace("*","")

        match = revar.match(decl)
        val = []
        if len(parts) > 1:
            parts[1] = parts[1].split("--")[0]
            val = parts[1].replace(";","")
            val = yaml.safe_load(val)

        if match:
            varType = match.group(1).strip()

            varName = match.group(2)

            arraySize = match.group(4) if match.group(4) else None

            cell = StackCell(varName)

            if "_t" in varType:
                varType = varType.replace("_t","")

            if varType not in sizeDict:
                return None

            
            if ptr:
                sizeBytes = 4
            else:
                sizeBytes = sizeDict.get(varType, 4)

            if arraySize:
                sizeBytes = sizeBytes * int(arraySize)
            
            size = int((sizeBytes + 3) / 4)

            cell.setWords(val)
            cell.setSize(size)
            cell.label = varName


            line = line.replace(match.group(0), 'local')


            return cell

        else:
            return None

