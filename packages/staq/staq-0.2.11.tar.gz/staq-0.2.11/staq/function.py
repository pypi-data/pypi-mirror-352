
import re



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

class FunctionArgument():
    def __init__(self, type : str, name:str):

        type = type.strip().replace("_t","")
        name = name.strip()

        self.name = name
        self.type = type
        self.size = 4

        if type in sizeDict:
            self.size = sizeDict[type]
        

class Function():
    def __init__(self, name, address = "???", args= [], type = 'void'):
        self.name = name
        self.address = address
        self.args = args 
        self.type = type
        self.locals = []
        self.calls = []
        self.raw = ""

    def addArgument(self, arg):
        self.args.append(arg)

    @classmethod
    def fromString(cls, line):
        
        #0x0040100 <int main(int, char**)>
        #int main(int argc, char **argv)
        #void doSomething(int a, int b)

        functionAddress = None

        regex = re.compile(r"(0x[0-9A-F]+)\S*?<(.*?)>")
        match = regex.match(line)

        if match:
            functionAddress = int(match.group(1), 16)
            line = match.group(2)
        

        #Parse the function definition
        regex = re.compile(r"(.*?[*]?)(\w+)\((.*?)\)")
        match = regex.match(line)

        if match:
            returnType = match.group(1).replace(" ","")
            functionName = match.group(2)
            args = match.group(3).split(',')

            functionArgs = []
            for arg in args:

                arg = arg.strip()

                if arg and arg != "...":
                    argParts = arg.split(' ')

                    if 'const' in argParts:
                        argParts.remove('const')

                    argType = argParts[0]
                    argName = None

                    if len(argParts) > 1:
                        argName = argParts[1]

                        while argName[0] == '*':
                            argType += '*'
                            argName = argName[1:]

                    functionArgs.append(FunctionArgument(argType, argName))
            
            ret = cls(functionName, functionAddress, functionArgs, returnType)
        
            return ret 

        else : 
            
            print(f"No match: {line}")

    def toYaml(self):
        return {
            'name': self.name,
            'address': self.address,
            'type': self.type,
            'args': [{'name': arg.name, 'type': arg.type} for arg in self.args],
            'locals': self.locals,
            'calls': self.calls
        }



def parseCFile(code):
    functions = []
    

    # Regular expressions to match function signatures, local variable declarations, and function calls
    function_re = re.compile(r'\b([A-Za-z_]\w*\s+\*?\s*\b[A-Za-z_]\w*\s*\([^)]*\)\s*)\{(.*?)}',re.DOTALL)

    call_re = re.compile(r'\b([A-Za-z_]\w*\s*\([^)]*\)\s*)')

    local_re = re.compile(r'(\w[\w\s\*]*\w)\s+(\w+)(\[(.*)\])?')

    defines_re = re.compile(r'#define\s+(\w+)\s+(\w+)')
    defines = {}

    define_matches = defines_re.finditer(code)

    for match in define_matches:
        defines[match.group(1)] = match.group(2)

        
    function_signatures = function_re.finditer(code)

    for match in function_signatures:
        signature = match.group(1).strip()
        function_body = match.group(2).strip()

        function = Function.fromString(signature)

        function.raw = match.group(0)


        
        if function:

            locals = local_re.finditer(function_body)


            for local in locals:
                
                if local.group(4) and local.group(4) in defines:
                    function.locals.append(f"{local.group(1)} {local.group(2)}[{defines[local.group(4)]}]")
                else:
                    function.locals.append(local.group(0))

            calls = call_re.finditer(function_body)

            for call in calls:
                function.calls.append(call.group(0))

            # function.locals = [var.strip() for var in local_re.findall(function_body)]
            # function.calls = [call.strip() for call in call_re.findall(function_body)]
            functions.append(function)

    return functions
