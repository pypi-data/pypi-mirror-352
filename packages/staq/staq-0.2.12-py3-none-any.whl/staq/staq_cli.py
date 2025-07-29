#!/bin/env python3
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import WordCompleter, PathCompleter, Completer
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, ScrollOffsets, FloatContainer,Float
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.mouse_events import MouseButton, MouseEvent, MouseEventType
from prompt_toolkit.widgets import TextArea, Frame, Label
from prompt_toolkit.history import FileHistory
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.widgets import HorizontalLine
from prompt_toolkit.data_structures import Point
from prompt_toolkit.document import Document
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit import print_formatted_text, ANSI
from prompt_toolkit.completion import NestedCompleter


import asyncio

import os
import argparse
import typing
import importlib.metadata
import builtins

from cliify.splitHelper import splitWithEscapes


from contextlib import contextmanager


from staq.stackSession import StackSession
from cliify.completers.prompt_toolkit import CommandCompleter


args = None
parser = None
session = StackSession()

version = importlib.metadata.version("staq")

completer = NestedCompleter.from_nested_dict(
    {
        "pop": None,
        "push" : {"--size": None, "--label": None, "--note": None}
    }
)

completion_lists = {
    "pop" : [],
    "ret" : [],
    "push" : ["--size ", "--label ", "--note ", "--address "],
    "frame" : ['--color '],
    "call": [],
    "function" : [],
    "load": [],
    "write": ["--address ", "--file "]
}


command_completer = CommandCompleter(session)

banner_text =f"Staq v{version}"



def accept(buff):
    global command_completer

    line = buff.text
    commands = splitWithEscapes(line, ";")

    for cmd in commands:
        
        cmd = cmd.strip()
        if cmd != "":
            session.tryParseCommand(cmd)


    if line == "":
        refreshOutput()

# Define key bindings
kb = KeyBindings()

# Exit application
@kb.add('c-c')
def exit_app(event):
    
    event.app.exit(0)

@kb.add('c-s')
def save_stack(event):
    session.parseCommand("save")
    pass

#pageup
@kb.add('c-right')
def page_up(event):
    session.stepForward()
    pass

#pagedown
@kb.add('c-left')
def page_down(event):
    session.stepBack()
    pass



def print_info(event):
    util_info.text = str(input_field.completer.words)
    pass


# Banner content

banner_left = Label(banner_text, style="fg:ansigreen")

top_info = Label("", style=" fg:ansired")
util_info = Label("", style="fg:ansiblue")

banner_right = HSplit([top_info])

#banner_right = Label("SimTime: 000000\nrepli-4h23\nconnected to .sdf.sdf", style="bg:ansiblack fg:ansired")

banner_content = VSplit([banner_left, banner_right])
# Divider line
divider = HorizontalLine()
divider.window.style = "fg:ansigreen"

# Main content area - initially empty, will be updated dynamically
_line_count =0
outputField = TextArea(multiline=True, style="bg:ansiblack fg:ansigreen")

def getCursPos():
    global _line_count
    return Point(x=0, y=_line_count)


output_control = FormattedTextControl( text=[('ansigreen', '')], get_cursor_position=getCursPos, focusable=True)
output_window = Window( content=output_control, style="class:main-content", wrap_lines= False, allow_scroll_beyond_bottom= True, scroll_offsets=ScrollOffsets(top = -100000, bottom=-100000))


# Input area
home_path = os.path.expanduser('~')
cmdHistory = FileHistory(home_path+'/.staq-history')

input_field = Buffer( multiline=False, complete_while_typing=True,history=cmdHistory, completer=command_completer)
input_window = Window(BufferControl(buffer=input_field), height=2, style='class:input-win')
prompt_window = Window(FormattedTextControl(text="$>"), height=1, style='fg:ansigreen', width=3)

input_field.accept_handler = accept


reg_control = FormattedTextControl( text=[('ansigreen', '')], get_cursor_position=getCursPos, focusable=True)

floating_window = Window(content=reg_control, style="class:main-content", wrap_lines= False, height=25, width=25) 

# Layout definition
layout = FloatContainer(
       content= HSplit([
        banner_content,  # Banner at the top
        divider,         # Divider line
        output_window,    # Main content area
        divider,         # Divider line
        # input_window,     # Input area at the bottom
        VSplit([prompt_window, input_window]) # Input area at the bottom
    ]),
    floats=[
        Float(xcursor=True,
              ycursor=True,
              content=CompletionsMenu(max_height=16, scroll_offset=1)),
        Float(top=2,
              right=1,
              content=floating_window)
    ]
)
# layout = HSplit([
#             banner_content,  # Banner at the top
#             divider,         # Divider line
#             output_window,    # Main content area
#             divider,         # Divider line
#             # input_window,     # Input area at the bottom
#             VSplit([prompt_window, input_window]) # Input area at the bottom
#         ])



# Initialize the argument parser
def init_args():
    global parser
    parser = argparse.ArgumentParser("Tool to simulate stack operations")
    parser.add_argument('-a', '--arch', type=str, help='Architecture to use', default="x86")
    parser.add_argument('-b', '--base-address', type=int, help='Stack Base Address', default=0xffff)
    parser.add_argument('-f', '--file', type=str, help='Stack File to load', default="")
    parser.add_argument('-i', '--init', type=str, help='Initial Stack File to load', default=".stackinit")
    parser.add_argument('-x', '--execute', nargs="*", type=str, help='Execute command', default="")




# Application
application = Application(layout=Layout(layout, focused_element=input_field), key_bindings=kb, full_screen=True ,mouse_support=True)

def refreshOutput():
    global prevRegLines
    global session
    
    text = session.stack.toAnsi(showAddress=True)
    regText = session.arch.registersToAnsi(width=floating_window.width -2)
    regAnsi = ANSI(regText)
    ansi = ANSI(text)

    top_info.text = session.status

    output_control.text = ansi
    reg_control.text = regAnsi






def printAnsi( text: str):
    
    ansi = ANSI(text)
    output_control.text = ansi

    pass



def printRedirect(*args, **kwargs):
    global outputText
    output = " ".join(map(str, args))

    outputText+= output

    ansi = ANSI(outputText)
    output_control.text = ansi


def clearConsole():
    global _line_count
    _line_count = 0
    output_control.text = [('ansigreen', '')]
    application.invalidate()

    pass


async def run():
    global parser
    global args
    global input_field
    global command_completer
    global session 

    init_args()
    args= parser.parse_args()

    #session.loadYaml("test/test1.stack.yml")

    session.stack.setBaseAddress( args.base_address)
    session.setArch(args.arch)

    banner_left.text = f"Staq v{version} - {args.arch} - {hex(args.base_address)}"
    

    #get list of subparsers from session parser 

    builtins.print = printRedirect
    session.print = printAnsi
    session.refreshOutput = refreshOutput


    if args.file != "":
        session.loadYaml(args.file)

    if os.path.exists(args.init):
        with open(args.init, 'r') as f:
            for line in f:
                session.tryParseCommand(line)

    if args.execute != "":
        line  = " ".join(args.execute)
        cmds = splitWithEscapes(line, ";")
        for cmd in cmds:
            session.tryParseCommand(cmd)

    


    
    refreshOutput()



    result = await application.run_async()


def main():
    asyncio.run(run())

if __name__ == '__main__':
   main()