staq
====

A terminal based application for visualizing stack operations and creating stack diagrams.


.. code::

    pip install staq 

cli
---

To run the cli; 

.. code:: 

    staq 


.. note:: When the CLI starts it will look for a file named `.stackinit` in the current directory and if it exists, it will run the commands in it.  This is useful for setting up a default environment.



This will start the cli interface. Here is a quick example of some commands: 

.. code:: 

    $> int etc[64] 
    $> call main(1,"hello")
    $> char buf[64] , note on local variable
    $> call strcpy(buf,argv[0])




.. image:: docs/assets/images/stack2.png


Because this is really just a tool for visualization, types are not strictly defined or used. For instance the following command is valid: 

.. code:; c 

    int i = index of buffer

It will add a word to the stack with label `i` and value "index of buffer"

Local vars
~~~~~~~~~~

you can declare local variables using standard C syntax.

.. code:: 

    char buffer[64]
    int i = 0x89

Loading a C file 
~~~~~~~~~~~~~~~~

You can load a file with C syntax to import functions. The functions will be loaded into the context including arguments, local variables, and calls to other functions.

.. code:: 

    load test.c


Write 
~~~~~

The `write` command lets you write data to the stack at a given address.

.. code:: 

    write 0x1000: [0x56, 0x78, 0x90, 0x12]

    #you can also use references to variables with offsets 
    write &buffer : [0x56, 0x78, 0x90, 0x12]
    write &buffer+4 : [0x56, 0x78, 0x90, 0x12]


Push 
~~~~

push will push a single `stack cell` onto the stack. A cell contains one or more words. Each cell can have a label, note, and words

.. code::

    push 0x56, arg1                  #Shortcut for 'push 0x56 , label: arg1'
    push label: buffer,  size: 64    #creates a 64 word cell with no specified data 
    push [1,2,3,4,5]                 #creates a 5 word cell with the values filled in 
    push <main+0x54> , note: return  #creates a single word on the stack with no label, and a note
    push {r0,r3,r7-r9 }              #pushes the registers r0, r3, r7, r8, and r9 onto the stack

Pop
~~~

pop will remove words from the stack 

.. code:: 

    pop             #remove a single word 
    pop esp         #remove a single word and set the register esp to the value popped
    pop 4           #remove 4 words 
    pop frame       #remove current frame 
    pop {r0-r3 }    #pops 4 words from the stack into the registers r0, r1, r2, and r3


Call 
~~~~

The `call` command will create a new stack frame and push the return address. If arguments are given, they will be pushed to the stack automatically.



Functions 
~~~~~~~~~

The ``call`` command gets run through a `CallingConvention` subclass (currently only cdecl is available) and performs operations according to the convention: 

- push arguments to stack 
- create a new stack frame 
- pushes return address 


You can declare functions to give the app context about argument type/size and labels, but you can also call arbitrary functions. It will just assume all arguments are a single row on the stack. 

.. code:: 

    function myFunction(int a, int b)
    call myFunction(41,32)

    call undeclaredFunction(1,2,3,4)     # Will assume all args are 32 bit values and label arg1, arg2, arg3, etc

.. note:: A lot of common functions from libc are already loaded in. 





run
~~~

The `run` command is similar to call, but it will continue calling the first known function call in each function until it runs out of calls or hits the `~~limit` arg. 


leave
~~~~~

The `leave` command will pop all local variables from the stack. This is the same as setting the stack pointer to the base of the current frame.


jmp
~~~

The `jmp` command will create a new stack frame and set the instruction pointer to the address given. It is similar to `call` but does not push args or a return address.

ret 
~~~

ret will pop one word and then perform a `jmp` to that address.


save 
~~~~

The `save` command will save the current state of the stack to a file. The extension will determine the format. currently `.html`, `.png`, and `.txt` are supported.

`.html` will save the stack as an interactive html file. 

`.png` will save the stack as a png image. 

`.txt` will save the stack as a text file containing all of the commands to recreate the stack.


example png output:


.. image:: docs/assets/images/stack3-out.png

.. note:: any unrecognized extension will default to `.txt`


.. warning:: Images are created with HTML which is then saved to a .png, which requires chrome to be installed. 


back/forward
~~~~~~~~~~~~

The session keeps a history of commands. You can move back and forward through the history with `ctrl+ left-arrow` and `ctrl+ right-arrow`



Sphinx extension
----------------

The package provides a Sphinx extension that allows you to add stack diaragrams to your documentation using the stack command structure



The `stack` directive can be used with inline code, or by pointing to a file 

.. code:: 

    .. stack:: 
        
        push ... , size: 256
        jmp main 
        char buf[64]
        call printf("Args: %d, %d", 12,34)

.. code::

    .. stack:: assets/diagrams/demo.staq 


