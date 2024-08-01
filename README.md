# mpPy6: Python Module for Multiprocess Communication with PySide6 UIs

mpPy6 (**M**ulti-**P**rocess **Py**side**6** Python module) is a Python module designed to facilitate communication between multiple processes while utilizing PySide for graphical user interfaces (GUIs). This module aims to provide a seamless solution for building applications with parallel processing capabilities and interactive UI components.
Features

* Multiprocess Communication: CMP enables efficient communication between multiple Python processes, allowing for concurrent execution of tasks.

* PySide Integration: CMP seamlessly integrates with PySide, a Python binding for the Qt framework, to create interactive and visually appealing user interfaces.

* Event Handling: CMP provides robust event handling mechanisms, allowing processes to communicate and synchronize events effectively.

# Installation

You can install 'mpPy6' using pip directly from this repo:
```bash
pip install git+https://github.com/agentsmith29/mpPy6.git@main
```

# Usage
The architecture is build, using two classes: [CProcess](./src/mpPy6/CProcess.py) and 
[CProcessControl](./src/mpPy6/CProcessControl.py). The *CProcess* class is used to create a child process, while the 
*CProcessControl* class is used to control the spawn child process. The *CProcessControl* class is responsible for 
registering the child process and defining the functions that will be executed in the child process. 
The *CProcess* class is responsible for executing the functions defined in the *CProcessControl* class.

## CProcess and CProcessControl
Construction of the class is straight forward and only requires inheritance from the *CProcess* and *CProcessControl* classes.
```python
class ChildProcess(mpPy6.CProcess):
    def __init__(self, state_queue, cmd_queue, kill_flag, *args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)
        
    # ... other code goes here
```
You see, that the *ChildProcess* class inherits from the *CProcess* class. The *CProcess* class requires three arguments
to be passed to the constructor. These are:
* state_queue: A queue object to send the state of the child process to the control class.
* cmd_queue: A queue object to receive commands from the control class.
* kill_flag: A flag to kill the child process.

The Control class is constructed in a similar way:
```python
class ChildProcessControl(mpPy6.CProcessControl):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Register the child process
        self.register_child_process(ChildProcess)
```
The *ChildProcessControl* class inherits from the *CProcessControl* class.
You just import your ChildProcess class and register it in the constructor of the *ChildProcessControl* class by using
the *register_child_process* method. All queues and flags are automatically created  and connected by the *CProcessControl* class.

### The Control function implementation
To add a function that can be executed in the child process, we now implement the very same function 
once in the *ChildProcessControl* class and once in the *ChildProcess* class. 
The function in the *ChildProcessControl* class only serves as a placeholder  or seceleton and does not need to contain 
any code. It is important that the signature of the function implemented here, also matches the signature of the function
implemented in the *ChildProcess* class.
```python 
# Create a body for your function. This does not necessarily have to include code, you can just print a message
# or add "pass", a comment, or a docstring.
@mpPy6.CProcessControl.register_function()
def add_two(self, num1: int, num2: int):
    print("I will add two numbers in a separate process")
```
What `@mpPy6.CProcessControl.register_function()` does is, that it wraps your function around a decorator, that will automatically
submit the function call to the command queue with all your parameters, to be exectued in the child process.

### The Process function implementation
In The *ChildProcess* class, we implement the function that will be executed in the child process. 
```python
    @mpPy6.CProcess.register_signal(signal_name='add_two_finished') # Explicitly set the signal name
    def add_two(self, num1: int, num2: int):
        # "return" automatically sends the result to the control class and triggers the signal with the
        # name "add_two_finished"
        return num1 + num2
```
You can see, that the function is decorated with `@mpPy6.CProcess.register_signal(signal_name='add_two_finished')` and 
has the same signature as the function in the *ChildProcessControl* class. 
The `return` statement will automatically send the result back to the control class and trigger the signal with the name
`add_two_finished`.
You do not neccessarily need to set a signal name. If omitted, the signal name will be the same as the function name with the 
postfix `_changed`, thus in this case `add_two_changed`.
```python
@mpPy6.CProcess.register_signal()
def add_two(self, num1: int, num2: int)
```
If you need to have an explicit postfix, you can set the `postfix` parameter in the decorator, the signal name will then be
`add_two_{postfix}`.
```python
@mpPy6.CProcess.register_signal(postfix="_ finished")
def add_two(self, num1: int, num2: int)
```
## Using properties
Sometimes it is usefule to act on a property change. E.g., the class controls a device and the device is connected or disconnected.
In this case you want to fire an event, if the device gets disconnected or connected. 
This can be achieved by using the `@mpPy6.CProperty` decorator.
```python
class ChildProcess(mpPy6.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag, *args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)

        self._myProperty = "Hello World!"

    @mpPy6.CProperty
    def myProperty(self):
        """ Returns if the laser is connected. """
        return self._myProperty

    @myProperty.setter('myProperty_changed')
    def myProperty(self, value: str):
        """ Sets the connected state of the laser. Only used internally by the process. """
        self._myProperty = value
```
The property can be changed internally, as you would do it with regular python getter annd setters. The neat part is however,
that you now just have to implement the correct Signal in the *ChildProcessControl* class and the signal will be triggered

```python 
class ChildProcessControl(mpPy6.CProcessControl):
    # Is emitted when the property myProperty in the Child is changed
    myProperty_changed = mpPy6.Signal(str, name='myProperty_changed')

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Register the child process
        self.register_child_process(ChildProcess)
```
## Construction, post-run initialization and destruction
The module has some special methods that can be implemented in the child process for handeling how the Child-Process
is constructed, initialized and destructed.
### Construction, post-run initialization
The child process self-initializes itself after the constructor is called. Due to the fact how multithreading works,
not everything can be initialized in the constructor. Objects that are not pickable (e.g., a logger object) can not be
initialized.
Thus, the CProcess implements a *postrun_init* method which is called after the constructor but before the process starts
its operation.
```python
def postrun_init(self):
    # Place it here (__init__ does not fully initialize the object), thus the post-run initialization
    # is necessary
    myObect = MyObject() # A object initialized after constructor
```
Not only initialization, but also function calls that should be executed after the constructor can be placed here.
The overloaded constructor ```__init__``` od the child process should only be used for variable definition. 

### Destruction
if the object is destructed, all queues and flags are automatically closed. If you need to do some cleanup, you can implement
the *cleanup* method in the child process.
```python
def cleanup(self):
    print("Exited ChildProcess...")
```



# Examples
Here's a simple example demonstrating how to use CMP:
## Examples 1: Simple addition
```python
import mpPy6

class ChildProcess(mpPy6.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag, *args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)

    # The signal (add_two_finished) name mus correspond to the signal in the control class "ChildProcessControl"
    # in order to get executed.
    # The function (add_two) and function's signature name must correspond to the function in the control class
    @mpPy6.CProcess.register_signal(signal_name='add_two_finished')
    def add_two(self, num1: int, num2: int):
        # "return" automatically sends the result to the control class and triggers the signal with the
        # name "add_two_finished"
        return num1 + num2


class ChildProcessControl(mpPy6.CProcessControl):
    add_two_finished = mpPy6.Signal(int, name='add_two_finished')

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Register the child process
        self.register_child_process(ChildProcess)

    # Create a body for your function. This does not necessarily have to include code, you can just print a message
    # or add "pass", a comment, or a docstring.
    @mpPy6.CProcessControl.register_function()
    def add_two(self, num1: int, num2: int):
        print("I will add two numbers in a separate process")
```
In this example, when the button is clicked, CMP emits the "button_clicked" event, which triggers the process_function to be executed in a separate process.
Contributing

## Example 2: Using properties
```python
import logging
import sys
import time
from random import random

from PySide6.QtWidgets import QApplication
from rich.logging import RichHandler

import mpPy6


class ChildProcess(mpPy6.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag, *args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)

        self._myProperty = "Hello World!"


    def postrun_init(self):
        # Place it here (__init__ does not fully initialize the object), thus the post-run initialization
        # is necessary
        self.set_myProperty("Hello World 2!")

    @mpPy6.CProperty
    def myProperty(self):
        """ Returns if the laser is connected. """
        return self._myProperty

    @myProperty.setter('myProperty_changed')
    def myProperty(self, value: str):
        """ Sets the connected state of the laser. Only used internally by the process. """
        self._myProperty = value

    def set_myProperty(self, value: str):
        # random sleep to simulate a process
        time.sleep(random() * 3 + 1) # sleep for 1 to 4 seconds
        self.myProperty = value


class ChildProcessControl(mpPy6.CProcessControl):
    # Is emitted when the property myProperty in the Child is changed
    myProperty_changed = mpPy6.Signal(str, name='myProperty_changed')

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Register the child process
        self.register_child_process(ChildProcess)
```





We welcome contributions from the community! If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request on the GitHub repository.

# License

This project is licensed under the GNU GENERAL PUBLIC LICENSE Version 3.0. See the LICENSE file for details.
