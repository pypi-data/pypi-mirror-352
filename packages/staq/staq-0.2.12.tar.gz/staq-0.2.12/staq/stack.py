import io
import os
import sys
import logging
from contextlib import redirect_stdout, redirect_stderr
from typing import List
from enum import Enum
from jinja2 import Environment, PackageLoader, select_autoescape

from termcolor import colored
import yaml
from PIL import Image

from staq.function import Function, FunctionArgument

from html2image import Html2Image


rich_color_map = {
    'grey': 'gray',
    'red': 'red',
    'green': 'green',
    'yellow': 'yellow',
    'blue': 'blue',
    'magenta': 'magenta',
    'cyan': 'cyan',
    'white': 'white',
    'dark_grey': 'grey53',
    'dark_red': 'maroon',
    'dark_green': 'dark green',
    'dark_yellow': 'olive',
    'dark_blue': 'navy',
    'dark_magenta': 'purple',
    'dark_cyan': 'teal',
    'dark_white': 'silver'
}

class StackWord():
    def __init__(self, cell, value = None):
        self.cell = cell
        self.value = value
        self.note = None
        self.noteColor = 'red'
        self.address = None

    def __str__(self):
        if self.value:
            return str(self.value)
        else:
            return " "
    

    def setNote (self, note, color = 'red'):
        self.note = note
        self.noteColor = color
        
    def isHead(self):
        return self.address == self.cell.frame.stack.pointer
    
    def shouldShow(self):
        return self.value or self.note or self.isHead() or (self.address == self.cell.address) or self.address in self.cell.frame.stack.argMarks 

    def toAnsi(self, width = 80, leftMargin = 20, color = "blue", showAddress = True):
        
        out = ""

        lmargin = " "*leftMargin

            

        lAddress = colored(f"{lmargin}")


        if showAddress and self.address:
            lAddress = colored(f"{hex(self.address).rjust(leftMargin)}", color="dark_grey")
            pass
        
        if self.isHead():
            strlen =  leftMargin - (len(str(hex(self.address))) + 3)
            pointer = colored(">>>", color="yellow") 
            strAddress = colored(hex(self.address), color="dark_grey")
            lAddress = " "*strlen + pointer + strAddress 
        
        out += lAddress + colored(f"│{str(self).ljust(width-2)}│", color=color)

        if self.address in self.cell.frame.stack.argMarks:
            out += colored(f"{self.cell.frame.stack.argMarks[self.address]}", "black","on_green")

        if self.note:
            out += colored(f" <-- {self.note}", color=self.noteColor)
        
        out += "\n"

        return out



class StackCell():
    def __init__(self, label = "", words=[], note=None, frame=None):
        self.address = None
        self.frame = None
        self.words: List[StackWord] = []
        self.size = 1
        self.label = label
        self.color = None

        if words:
            self.setWords(words)
            self.size = len(words)



    def setSize(self, size):
        size = int(size)
        self.size = size
        while(len(self.words) < size):
            self.words.append(StackWord(self))

    def setWords(self,words, offset = 0):



        #if not a list, make it a list
        if not isinstance(words, list):
            words = [words]

        self.setSize(len(words))



        for word in words:

            if word != "" and word != " " and offset < self.size:

                if isinstance(word, StackWord):
                    self.words[offset] = word
                else:
                    self.words[offset].value = word
                offset += 1


    def setNote (self, note):
        self.words[0].note = note

    def applyAddresses(self, baseAddress):

        self.address = baseAddress

        for word in self.words:
            word.address = baseAddress
            baseAddress += (self.frame.stack.bits // 8)

        return baseAddress
    
    @classmethod
    def fromObj(cls, obj):

        ret = StackCell()

        if not isinstance(obj, dict):
            ret.setWords(obj)
        
        else:

            key = list(obj.keys())[0]
            value = obj[key]

            ret.label = key

            if not isinstance(value, dict):
                ret.setWords(value)

            else:

                if 'words' in value:
                    ret.setWords(value['words'])
                else:
                    ret.words = []

                if 'color' in value:
                    ret.color = value['color']

                if 'note' in value:
                    ret.note = value['note']

                if 'size' in value:
                    ret.setSize(value['size'])



        return ret
    
    def toAnsi(self, width = 80, leftMargin = 20, color = "blue", showAddress = True, sof = False):

        out = ""

        lmargin = " "*leftMargin

        lAddress = colored(f"{lmargin}")

        if showAddress and self.address:
            lAddress = colored(f"{hex(self.address).rjust(leftMargin)}", color="dark_grey")
            pass

        if self.color:
            color = self.color

        top = f"├{'─'*(width-2)}┤"

        header = self.label

        if self.size > 1:
            header = f"{self.label} [{self.size * (self.frame.stack.bits // 8)}]"

        if header and header != "":
            
            top = f"├{header.center(width-2,'─')}┤"

            topParts = top.split(header)

            top = colored(topParts[0], color=color) + colored(header, color="dark_grey") + colored(topParts[1], color=color)

            if sof:
                top = f"┌{header.center(width-2,'─')}┐"
        
        else:
            if sof:
                top = f"┌{'─'*(width-2)}┐"
        

        out += colored(f"{lmargin}{top}\n", color=color)


        showIndexes = []
        emptyStreak = 0

        for i in range(self.size):

            if self.words[i].shouldShow() :
                showIndexes.append(i)
                emptyStreak = 0
            else:
                emptyStreak += 1

            if emptyStreak == 1:
                showIndexes.append(None)

            # if emptyStreak < 2:
            #     showIndexes.append(i)

        for i in showIndexes:

            if i is None:
                out+= colored(f"{lmargin}:{' '*(width-2)}:\n", color=color)
            else: 
                word = self.words[i]

                out+= word.toAnsi(width, leftMargin, color, showAddress)




        return out




class StackFrame():
    def __init__(self, name=None, function :Function = None):
        self.name = name
        self.function = function
        self.cells: List[StackCell] = []
        self.color = None
        self.stack = None
        self.basePointer = 0
        

    def length(self):
        return len(self.cells)

    def pop(self):


        if len(self.cells) == 0:
            return False
        
        ret = "???"
        cell = self.cells[-1]

        if cell.size == 1:
            if len(cell.words) > 0:
                ret = cell.words.pop(0)
            self.cells.pop()
        else :
            if(len(cell.words) > 0):
                ret = cell.words.pop(0)
            cell.size -= 1
        
        return ret
        
    
    def push(self, cell):
        
        cell.frame = self
        self.cells.append(cell)

    def applyAddresses(self, baseAddress = 0x07f00000):

        for cell in self.cells:
            baseAddress = cell.applyAddresses(baseAddress)
 
        
        return baseAddress
            

    @classmethod
    def fromObj(cls, obj, order = 'normal'):
            
        ret = cls()

        if 'function' in obj:
            ret.function = obj['function']
            ret.color = "blue"
        
        if 'stack' in obj:
            cells = []
            if order == 'normal':
                cells = reversed(obj['stack'])
            else:
                cells = obj['stack']

            for cell in cells:
                ret.push(StackCell.fromObj(cell))

        if 'color' in obj:
            ret.color = obj['color']

        return ret
    
    def toAnsi(self, width = 80, leftMargin = 20, color= "blue", showAddress = False):

        #           ╭─main──────────────────────────────╮
        #  0x070000 │         i = 0x014                 │
        #           ├─────────────buffer────────────────┤
        #  0x070000 :        ...                        :
        #           ├─────────────arg1──────────────────┤
        #  0x070000 │         32                        | 
        #           ├──────────────arg1─────────────────┤
        #  0x070000 │         14                        │
        #           ╰──────────────arg2─────────────────╯

        out = ""

        lmargin = " "*leftMargin
        fill = "─"*(width - 2)

        if not self.function:
            color = "dark_grey"

        if self.color:
            color = self.color


        if self.function:
            fill = "─"*(width - (len(self.function.name) + 3))
            out += colored(f"{lmargin}╭─{self.function.name}{fill}╮\n", color=color)
        # else: 
        #     out += colored(f"{lmargin}┌{fill}┐\n",color=color)
        
        for i,cell in enumerate( reversed(self.cells)):
           
           sof = False
           if i == 0 and not self.function:
                sof = True
           out += cell.toAnsi(width, leftMargin, color, sof=sof,showAddress=showAddress)

        if self.function:
            fill = "─"*(width - 2)
            out += colored(f"{lmargin}╰{'─'*(width - 2)}╯\n", color=color)
        else:
            out += colored(f"{lmargin}└{fill}┘\n",color=color)

        return out
        


class Stack():
    def __init__(self, baseAddress = 0xffff):
        self.frames: List[StackFrame] = []
        self.currentFrame = None
        self.bits = 32
        self.baseAddress = baseAddress
        self.endian = 'little'
        self.pointer = self.baseAddress
        self.argMarks = {}

    def setBaseAddress(self, baseAddress):

        offset = baseAddress - self.baseAddress
        self.pointer += offset
        self.baseAddress = baseAddress

        self.applyAddresses()

    def nextAddress(self):

        offset = self.bits // 8
        return self.pointer + offset


    def movePointer(self, wordCount):

        byteCount = wordCount * (self.bits // 8)
        self.pointer += byteCount

    def resolveAddress(self, address):

        if isinstance(address, str):

            if address.endswith(":"):
                address = address[:-1]


            if address.startswith("&"):
                var = address[1:]
                offset = 0
                if '+' in var:
                    parts = var.split('+')
                    var = parts[0]
                    offset = int(parts[1])
                
                if '-' in var:
                    parts = var.split('-')
                    var = parts[0]
                    offset = -1 * int(parts[1])


                for frame in reversed(self.frames):
                    for cell in reversed(frame.cells):
                        if cell.label == var:
                            return cell.address + offset


            elif address.startswith("0x"):
                return int(address, 16)
            else:
                return int(address)
        else:
            return address
        
    def getCells(self) -> List[StackCell]:
        cells = []
        for frame in reversed(self.frames):
            for cell in reversed(frame.cells):
                cells.append(cell)
        return cells
        
    def getCell(self, address):
            
        for frame in self.frames:
            for cell in frame.cells:

                start = cell.address
                end = cell.address+ (cell.size * (self.bits//8))

                if (address >= start) and (address < end):
                    return cell

            
        return None
        
    def getWord(self, address):
            
            cell = self.getCell(address)
            if cell:
                offset = int((address - cell.address) // (self.bits // 8))

                return cell.words[offset]
            else:
                return None

    def write(self, values, address = None):

        if not isinstance(values, list):
            values = [values]

        if not address:
            address = self.pointer
        else:
            address = self.resolveAddress(address)
        
        for value in values:
            

            word = self.getWord(address)
            if word:
                word.value = value

                address += (self.bits // 8)

    def setNote (self, note, address = None, color = 'red'):

        if not address:
            address = self.pointer
        else:
            address = self.resolveAddress(address)

        word = self.getWord(address)
        if word:
            word.setNote(note,color)
    
    def popFrame(self):
        
        if self.currentFrame:

            count = 0

            for cell in self.currentFrame.cells:
                count += cell.size 

            self.movePointer(count)
        
            self.frames.pop()

            if len(self.frames ) > 0:
                self.currentFrame = self.frames[-1]
            else:
                self.currentFrame = None

    def pushFrame(self, frame):
        frame.stack = self
        frame.basePointer = self.pointer -1
        self.frames.append(frame)
        self.currentFrame = self.frames[-1]

    def clear(self):
        self.frames = []
        self.currentFrame = None
        self.pointer = self.baseAddress

    def popLocals(self):

        if self.currentFrame:

            while self.currentFrame.length() > 1:
                self.currentFrame.pop()

    def pop(self, count = 1):

        ret = None
        while count > 0:
            if self.currentFrame:

                ret = self.currentFrame.pop()
                if ret is not None:
                    self.movePointer(1)
                    count -= 1
                if self.currentFrame.length() == 0:
                    self.popFrame()
            else:

                return ret


            
        
        return ret

    
    def push(self, cell: StackCell):

        if not self.currentFrame:
            self.pushFrame(StackFrame())

        self.currentFrame.push(cell)
        self.movePointer(-1 * cell.size)

        self.currentFrame.cells[-1].applyAddresses(self.pointer)


        
    def call(self, function , args):

        if isinstance(function, Function):
            self.frames.append(StackFrame(function.name))
        else:
            self.frames.append(StackFrame(function))

    def applyAddresses(self, baseAddress = None):

        if not baseAddress:
            baseAddress = self.baseAddress

        self.nextAddr = baseAddress
        for frame in self.frames:
            self.nextAddr = frame.applyAddresses(self.nextAddr)

        return self.nextAddr
    
    def loadYaml(self, obj):
        

        if isinstance(obj, str):
            with open(obj) as f:
                obj = yaml.safe_load(f)
        
        if 'stackBase' in obj:
            self.baseAddress = obj['stackBase']
        
        if 'order' in obj:
            order = obj['order']

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
                    self.pushFrame(frame)
                    self.currentFrame = None
                else:
                        cell = StackCell.fromObj(node)
                        self.push(cell)
        
        self.applyAddresses()

    def getLeftMargin(self, showAddress = True):

        margin = 3 # room for pointer >>> 

        if showAddress:
            
            h = hex(self.baseAddress) #this is the longest it will be 
            margin += len(h) + 2 #room for 0x

        return margin

    
    def toAnsi(self, width = 50, showAddress = False, leftMargin = None):
     
        # Another style 
        #           ╭─vuln──────────────────────────────╮
        #  0x070000 │                                   │
        #           ├───────────────────────────────────┤
        #  0x070000 │                                   | 
        #           ├───────────────────────────────────┤
        #  0x070000 │   <main+054>                      │ <- return to main
        #           ╰───────────────────────────────────╯
        #           ╭─main──────────────────────────────╮
        #           ├───────────────i───────────────────┤
        #  0x070000 │ 0x014                             │
        #           ├─────────────buffer────────────────┤
        #           :                                   : 
        #  0x070000 :  ...                              : 
        #           ├───────────────arg1────────────────┤
        #  0x070000 │ 17                                | 
        #           ├───────────────arg2────────────────┤
        #  0x070000 │ 38                                │
        #           ╰───────────────────────────────────╯
        #           ┌───────────────────────────────────┐
        #  0x070000 │     . . .                         │
        #           └───────────────────────────────────┘


        if leftMargin == None:
                leftMargin = self.getLeftMargin(showAddress)

        out = ""
        for i,frame in enumerate(reversed(self.frames)):
            
            color = "blue"
            if frame == self.currentFrame:
                color = "green"

            out += frame.toAnsi(width,color=color, showAddress=showAddress, leftMargin=leftMargin)

        #Add end of stack

        if showAddress:
            out+= colored(f"{hex(self.baseAddress).rjust(leftMargin)}", color="dark_grey")
        else:
            out += colored(f'{" "*(leftMargin)}', color="dark_grey")
        out += colored(f' {"End Of Stack".center((width-2), "─")}\n', color="dark_grey")

        return out


    

    
    def toHtml(self, showAddress = True, full = False):
        env = Environment(
            loader=PackageLoader('staq', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('stack.html.j2')
        if full:
            template = env.get_template('stack-full.html.j2')
        html_output = template.render(stack=self, showAddress = showAddress)
        return html_output

    
    def print(self, showAddress= True, leftMargin = 20):
        
        ascii = self.toAnsi(showAddress=showAddress, leftMargin=leftMargin)
        print(ascii)
        
    
    def generatePng(self, filePath = 'out.png', width = None):

        html = self.toHtml()

        ansi = self.toAnsi( showAddress=False)
        width = width 


        lines = ansi.count('\n')

        path, name = os.path.split(filePath)


        #This will fail if chrome is not installed
        hti = Html2Image()



        # Create a string buffer to capture stdout and stderr
        f = io.StringIO()

        # Redirect stdout and stderr
        with redirect_stdout(f), redirect_stderr(f):
            hti.output_path = path
            hti.screenshot(html_str=html, save_as=name)

        #crop the image
        with Image.open(filePath) as img:
            img = img.convert("RGBA")
            
            #crop the image to remove the extra whitespace
            bbox = img.getbbox()

            #add some padding to all side 
            padding = 10
            bbox = (bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding)


            img = img.crop(bbox)

            if width:
                currWidth = img.width
                currHeight = img.height

                #assume pixels
                newWidth = width
                newHeight = int((newWidth/currWidth) * currHeight)

                if isinstance(width, str):
                    if width.endswith("%"):
                        newWidth = int((int(width[:-1])/100) * currWidth)
                        newHeight = int((int(width[:-1])/100) * currHeight)
                    if width.endswith("px"):
                        newWidth = int(width[:-2])
                        newHeight = int((newWidth/currWidth) * currHeight)

                img = img.resize((newWidth, newHeight))

                    


            img.save(filePath)


        
