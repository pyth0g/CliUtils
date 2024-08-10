import random
import time
import msvcrt
import threading
import itertools
from PIL import Image
from typing import Any, Iterable, Callable
import cv2
import keyboard
import os
import subprocess
import re
import statistics

last_str = ""

class ReturnThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None) -> None:
        threading.Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None

    def run(self) -> None:
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)

    def join(self) -> Any:
        threading.Thread.join(self)
        return self._return

class OverPrint:
    printing = True
    def __init__(self) -> None:
        pass

    last_nrows = None
    def _csi(values: list) -> None:
        csi_up = f"\x1B[{OverPrint.last_nrows}A"
        csi_clr= "\x1B[0K"
                
        if OverPrint.last_nrows is None:
            csi_up = ""
        else:
            if OverPrint.last_nrows > len(values):
                print(f'{csi_up}{csi_clr}')
                for r in range(1,OverPrint.last_nrows): print(f'{csi_clr}')
                
        OverPrint.last_nrows = len(values)
        print(f'{csi_up}{values[0]}{csi_clr}')
        for r in range(1, len(values)): print(f'{values[r]}{csi_clr}')

class str(str):
    def back_replace(string: str, old: str, new: str) -> str:
        head, _sep, tail = string.rpartition(old)
        return head + new + tail

def silent(func, *args: Any) -> Any:
    """
    Run any function in this library to without displaying their output in the console.
    """
    OverPrint.printing = False
    r = func(*args)
    OverPrint.printing = True
    return r

def pprint(*values: object, sep: str = " ", nl_sep: str = "\n") -> None:
    """
    Grants the ability to print on the same lines multiple times.\n
    When you are done you can use 'cprint' or 'lock' to lock the print in (so it doesn't get replaced by future pprint calls)
    """
    if OverPrint.printing:
        global last_str
        for value in values:
            if len(values) > 1:
                last_str += str(value) + str(sep) if value != values[-1] else str(value)
                OverPrint._csi(last_str.split(nl_sep))
            else:
                OverPrint._csi(str(value).split(nl_sep))

def nprint(*values: object, lock: bool = True, padding: int = 0) -> None:
    """
    Prints values given next to each other with pprint and locks it by default (giving the same behavior as cprint).
    """
    pprint(nget(*values, padding=padding))
    if lock:
        global last_str
        last_str = ""
        OverPrint.last_nrows = None

def nget(*values: object, padding: int = 0) -> str:
    """
    Returns values given next to each other as string.
    """
    if OverPrint.printing:
        values = list(map(lambda t: t + " " * padding, values))
        values[-1] = str(values[-1]).back_replace(" " * padding, "") if padding != 0 else values[-1]
        lines = [arg.split("\n") for arg in values]
        max_lines = max(len(line) for line in lines)

        for line in lines:
            while len(line) < max_lines:
                line.append(" " * padding)

        display_lines = ["".join(parts) for parts in zip(*lines)]
            
        display = "\n".join(display_lines)
            
        return display

def lock() -> None:
    """
    Clears the pprint functions data so it doesn't override future prints.
    """
    global last_str
    last_str = ""
    OverPrint.last_nrows = None

def cprint(*values: object, sep: str = " ", nl_sep: str = "\n") -> None:
    """
    Use pprint to print the value (print can sometimes be unreliable with pprint) and then call lock.
    """
    if OverPrint.printing:
        pprint(*values, sep=sep, nl_sep=nl_sep)
        lock()

def flush_input() -> None:
    """
    Flushes the input stream.
    """
    while msvcrt.kbhit():
        msvcrt.getch()

class SelList:
    def __init__(self, values: list, type: str = "chr", end: str = ")", start_index: int = 1, sel_start: str  = "\033[1m", sel_end: str = "\033[0m", sep: str = " ", kbd: bool = True) -> None:
        """
        values      - this is a list off all the values in list (Eg values=["val_1"]: a) val_1 ).\n
        type        - are the list indicators numbers (num) or characters (chr). (Eg. type="num": 1), 2), 3), ...).\n
        end         - endings for the list indicators (Eg. end=".": 1., 2., 3., ...).\n
        start_index - at what index the list starts.\n
        sel_start   - the value of sel will be prepended to the selected item.\n
        sel_end     - the value will be appended to the selected item.\n
        sep         - separator between the list indicator and value.\n
        kbd        - wether to use the keyboard module (not 'pure' cli but more reliable (works pretty much everywhere)) or msvcrt.getch() ('pure' cli but less reliable (might not work everywhere))
        """
        self.type = type
        self.end = end
        self.list = ""
        self.index = start_index
        self.len = 0
        self.sel = [sel_start, sel_end]
        self.values = values
        self.sep = sep
        self.kbd = kbd

        for i in values:
            self._add(i)

    class DisplayType:
        ARROW = "arrow"
        KEY = "key"

    class Type:
        CHR = "chr"
        NUM = "num"

    def _add(self, value: str) -> None:
        """
        value - what value to add to the list (Eg. value="example": a) example )
        """

        if self.type == "chr":
            self.list += f"{chr(96 + self.index)}{self.end}{self.sep}{value}\n"

        if self.type == "num":
            self.list += f"{self.index}{self.end}{self.sep}{value}\n"

        self.index += 1
        self.len += 1

    def get(self) -> str:
        """
        Returns the list as a string.
        """
        
        return self.list
    
    def _display(self, sel: int) -> str:
        new_list = []
        for c, i in enumerate(self.list.split("\n")):
            if c == sel:
                new_list.append(f"{self.sel[0]}{i}{self.sel[1]}")

            else:
                new_list.append(i)

        return "\n".join(new_list)[:-1]
    
    def _display_msvcrt(self, key_delay: float = 0.15) -> str:
        sel = 0

        pprint(self._display(sel))
        while True:
            key = ord(msvcrt.getch())
            if key == 13:
                break

            if key == 0:
                key = ord(msvcrt.getch())
                if key == 80:
                    if sel < self.len - 1: sel += 1 
                    else: sel = 0
                    pprint(self._display(sel))
                    time.sleep(key_delay)

                elif key == 72:
                    if sel > 0: sel -= 1 
                    else: sel = self.len - 1
                    pprint(self._display(sel))
                    time.sleep(key_delay)                

        time.sleep(key_delay)
        flush_input()
        cprint(self._display(sel))

        return self.values[sel]
    
    def _display_keyboard(self, key_delay: float = 0.15) -> str:
        sel = 0

        pprint(self._display(sel))
        while True:
            if keyboard.is_pressed("DOWN ARROW"):
                if sel < self.len - 1: sel += 1 
                else: sel = 0
                
                pprint(self._display(sel))
                time.sleep(key_delay)

            elif keyboard.is_pressed("UP ARROW"):
                if sel > 0: sel -= 1 
                else: sel = self.len - 1

                pprint(self._display(sel))
                time.sleep(key_delay)

            elif keyboard.is_pressed("ENTER"):
                break

        time.sleep(key_delay)
        flush_input()
        cprint(self._display(sel))

        return self.values[sel]

    def display(self, type: str | None = None, key_delay: float = 0.15, allowed: Callable = None) -> str:
        """
        type      - the type of selection SelList.ARROW to use arrow keys for selection, SelList.KEY to type the indicator of the selection.\n
        key_delay - the delay between checking for key presses.\n
        allowed   - function that will be passed to the filter for the preview character. Leave None for auto.
        """

        auto = True if not allowed else False

        if type == self.DisplayType.ARROW or not type:
            if self.kbd:
                return self._display_keyboard(key_delay)

            else:
                return self._display_msvcrt(key_delay)

        elif type == self.DisplayType.KEY:
            if self.type == self.Type.CHR:
                allowed = lambda t: str(t).isalpha()

            elif self.type == self.Type.NUM:
                allowed = lambda t: str(t).isnumeric()          

            print(self.list)
            prev = " "
            prev_i = None
            prev_int = None
            Ansi.Cursor.hide()
            while True:
                print(f"[{prev}]")
                prev_u = msvcrt.getch().decode()
                if prev_u != "\r" and len(list(filter(allowed, prev_u))) == 1:
                    if auto:
                        if str(prev_u).isalpha():
                            prev_i = ord(prev_u) - 96

                        elif str(prev_u).isnumeric():
                            prev_i = int(prev_u)

                        if isinstance(prev_i, int):
                            if prev_i > 0 and prev_i <= len(self.values):
                                prev = prev_u
                                prev_int = prev_i

                if prev_u == "\r":
                    if not prev_int:
                        Ansi.Cursor.up()
                        continue

                    if prev_int:
                        break

                Ansi.Cursor.up()
            Ansi.Cursor.show()

            flush_input()

            return self.values[prev_int - 1]
        
class Selection:
    def __init__(self, values: list, prepend: str = "> ", append: str = "", sel_prepend: str  = "\033[1m> ", sel_append: str = "\033[0m", kbd: bool = True) -> None:
        """
        values      - this is a list off all the values in list (Eg values=["val_1"]: > val_1 ).\n
        prepend     - the string that will be prepended to the non selected item.\n
        append      - the string that will be appended to the non selected item.\n
        sel_prepend - the value that will be prepended to the selected item.\n
        sel_append  - the value that will be appended to the selected item.\n
        kbd         - use the keyboard module (not 'pure' cli but more reliable (works pretty much everywhere)) or msvcrt.getch() ('pure' cli but less reliable (might not work everywhere))
        """
        self.prepend = prepend
        self.append = append
        self.sel_prepend = sel_prepend
        self.sel_append = sel_append
        self.list = ""
        self.len = 0
        self.values = values
        self.kbd = kbd
        self.index = 0
        self.values = values

        for i in self.values:
            self._add(i, 0)

    def _add(self, value: str, sel) -> None:
        """
        value - what value to add to the list (Eg. value="example": > example)
        """

        self.list += f"{self.sel_prepend if self.index == sel else self.prepend}{value}{self.sel_append if self.index == sel else self.append}\n"

        self.index += 1
        self.len += 1

    def get(self) -> str:
        """
        Returns the list as a string.
        """
        
        return self.list
    
    def _display(self, sel) -> str:
        self.list = ""
        self.len = 0
        self.index = 0
        for i in self.values:
            self._add(i, sel)

        return self.list[:-1]
    
    def _display_msvcrt(self, key_delay: float = 0.15) -> str:
        sel = 0

        pprint(self._display(sel))
        while True:
            key = ord(msvcrt.getch())
            if key == 13:
                break

            if key == 0:
                key = ord(msvcrt.getch())
                if key == 80:
                    if sel < self.len - 1: sel += 1 
                    else: sel = 0
                    pprint(self._display(sel))
                    time.sleep(key_delay)

                elif key == 72:
                    if sel > 0: sel -= 1 
                    else: sel = self.len - 1
                    pprint(self._display(sel))
                    time.sleep(key_delay)                

        time.sleep(key_delay)
        flush_input()
        cprint(self._display(sel))

        return self.values[sel]
    
    def _display_keyboard(self, key_delay: float = 0.15) -> str:
        sel = 0

        pprint(self._display(sel))
        while True:
            if keyboard.is_pressed("DOWN ARROW"):
                if sel < self.len - 1: sel += 1 
                else: sel = 0
                
                pprint(self._display(sel))
                time.sleep(key_delay)

            elif keyboard.is_pressed("UP ARROW"):
                if sel > 0: sel -= 1 
                else: sel = self.len - 1

                pprint(self._display(sel))
                time.sleep(key_delay)

            elif keyboard.is_pressed("ENTER"):
                break

        time.sleep(key_delay)
        flush_input()
        cprint(self._display(sel))

        return self.values[sel]

    def display(self, key_delay: float = 0.15) -> str:
        """
        key_delay - the delay between checking for key presses.\n
        """

        if self.kbd:
            return self._display_keyboard(key_delay)

        else:
            return self._display_msvcrt(key_delay)

class List:
    def __init__(self, values: list, type: str = "chr", end: str = ")", start_index: int = 1, sep: str = " ") -> None:
        """
        values      - this is a list off all the values in list (Eg values=["val_1"]: a) val_1 ).\n
        type        - are the list indicators numbers (num) or characters (chr). (Eg. type="num": 1), 2), 3), ...).\n
        end         - endings for the list indicators (Eg. end=".": 1., 2., 3., ...).\n
        start_index - at what index the list starts.\n
        sep         - separator between the list indicator and value.
        """
        self.type = type
        self.end = end
        self.list = ""
        self.index = start_index
        self.len = 0
        self.values = values
        self.sep = sep

        for i in values:
            self._add(i)

    def _add(self, value: str) -> None:
        """
        value - what value to add to the list (Eg. value="example": a) example )
        """

        if self.type == "chr":
            self.list += f"{chr(96 + self.index)}{self.end}{self.sep}{value}\n"

        if self.type == "num":
            self.list += f"{self.index}{self.end}{self.sep}{value}\n"

        self.index += 1
        self.len += 1

    def get(self) -> str:
        """
        Returns the list as a string.
        """
        
        return self.list[:-1]
    
    def display(self) -> None:
        """
        Displays the list.
        """
        cprint(self.get())

class Draw:
    class FullCircle:
        def __init__(self, size: str, edge = "@", bg: str = " ") -> None:
            """
            size - diameter of the circle (Eg. size=12 creates a circle with d=12 and r=6).\n
            edge - the edge (and filling) of the circle.\n
            bg   - the background of the canvas.
            """
            self.size = size
            self.e = edge
            self.bg = bg

        def get(self) -> str:
            """
            Return the circle as a string.
            """
            diameter = self.size

            radius = diameter / 2 - .5
            r = (radius + .25)**2 + 1

            circle = ""

            for i in range(diameter):
                y = (i - radius)**2
                for j in range(diameter):
                    x = (j - radius)**2
                    if x + y <= r:
                        circle = circle + f"{self.e} "
                    else:
                        circle = circle + self.bg * 2
                circle = circle + '\n'

            return circle[:-1]
        
        def display(self) -> None:
            """
            Display the circle.
            """
            cprint(self.get())

    class Circle:
        def __init__(self, size: int, edge = "@", bg: str = " ") -> None:
            """
            size - diameter of the circle (Eg. size=12 creates a circle with d=12 and r=6).\n
            edge - the edge of the circle.\n
            bg   - the background of the canvas.
            """
            self.size = size
            self.e = edge
            self.bg = bg

        def get(self) -> str:
            """
            Return the circle as a string.
            """
            diameter = self.size
            radius = diameter / 2 - 0.5
            r_outer = (radius + 0.5)**2
            r_inner = (radius - 0.5)**2

            circle = ""

            for i in range(diameter):
                y = (i - radius)**2
                for j in range(diameter):
                    x = (j - radius)**2
                    if r_inner <= x + y <= r_outer:
                        circle += f"{self.e} "
                    else:
                        circle += self.bg * 2
                circle += '\n'

            return circle[:-1]
        
        def display(self) -> None:
            """
            Display the circle.
            """
            cprint(self.get())

    class Triangle:
        def __init__(self, size: int, slant: list[str] = ["/", "\\"], floor: str = "_") -> None:
            """
            size  - the size of the bottom line of the right triangle (Eg. size=6).\n
            slant - the characters used for the slants (Eg. slant=["/","\\"]).\n
            floor - the character used for the bottom line of the triangle (Eg. floor="_").
            """
            self.size = size
            self.f = floor
            self.s = slant

        def get(self) -> str:
            """
            Return the triangle as a string.
            """
            t = f"{" " * (self.size + 1)}{self.s[0]}{self.s[1]}\n"
            s = 0
            for c in range(self.size):
                t += f"{" " * (self.size - c)}{self.s[0]}{" " * s}{" " * (c + 2)}{self.s[1]}\n"
                s += 1

            t += f"{self.s[0]}{self.f * s}{self.f * (self.size + 2)}{self.s[1]}"

            return t
        
        def display(self) -> None:
            """
            Display the triangle
            """
            cprint(self.get())

    class FullTriangle:
        def __init__(self, size: int, edge: str = "@", fill: str = "*") -> None:
            """
            size  - the size of the bottom line of the right triangle (Eg. size=6).\n
            slant - the characters used for the slants (Eg. slant=["/","\\"]).\n
            fill - the character used for the inside of the triangle including the bottom line (Eg. fill="*").
            """
            self.size = size
            self.e = edge
            self.f = fill

        def get(self) -> str:
            """
            Return the triangle as a string.
            """
            t = f"{" " * (self.size + 1)}{self.e}{self.e}\n"
            s = 0
            for c in range(self.size):
                t += f"{" " * (self.size - c)}{self.e}{self.f * s}{self.f * (c + 2)}{self.e}\n"
                s += 1

            t += f"{self.e}{self.e * s}{self.e * (self.size + 2)}{self.e}"

            return t
        
        def display(self) -> None:
            """
            Display the triangle
            """
            cprint(self.get())

    class Rectangle:
        def __init__(self, w: int, h: int, edges: list[str] = ["┌", "┐", "└", "┘"], sides: list[str] = ["─", "│"]) -> None:
            """
            w     - width of the rectangle (Eg. w=6).\n
            h     - height of the rectangle (Eg. h=6).\n
            edges - list of edges for the rectangle (Eg. edges=["┌", "┐", "└", "┘"]).\n
            sides - list of sides for the rectangle (Eg. sides=["─", "│"]).
            """
            self.size = (w - 2, h - 2)
            self.edges = edges
            self.sides = sides

        def get(self) -> str:
            """
            Return the rectangle as a list.
            """
            box = f"{self.edges[0]}{self.sides[0]*(self.size[0])}{self.edges[1]}\n"
            for _ in range(self.size[1]):
                box += f"{self.sides[1]}{" " * self.size[0]}{self.sides[1]}\n"

            box += f"{self.edges[2]}{self.sides[0]*(self.size[0])}{self.edges[3]}"

            return box
        
        def display(self) -> None:
            """
            Display the rectangle.
            """
            cprint(self.get())

    class FullRectangle:
        def __init__(self, w: int, h: int, edge: str = "@", fill: str = "+") -> None:
            """
            w    - width of the rectangle (Eg. w=6).\n
            h    - height of the rectangle (Eg. h=6).\n
            edge - the edge character for the rectangle (Eg. edge="@").\n
            fill - character that will fill the rectangle (Eg. fill="+").
            """
            self.size = (w - 2, h - 2)
            self.e = edge
            self.f = fill

        def get(self) -> str:
            """
            Return the rectangle as a list.
            """
            box = f"{self.e*(self.size[0] + 2)}\n"
            for _ in range(self.size[1]):
                box += f"{self.e}{self.f * self.size[0]}{self.e}\n"

            box += f"{self.e*(self.size[0] + 2)}"

            return box
        
        def display(self) -> None:
            """
            Display the rectangle.
            """
            cprint(self.get())

class Container:
    class Box:
        def __init__(self, value: str, edges: list[str] = ["┌", "┐", "└", "┘"], sides: list[str] = ["─", "│"], padding: int = 1) -> None:
            """
            value   - the text that will be put in the rectangle.\n
            edges   - the string for each edge of the rectangle.\n
            sides   - the strings for the two sides of the rectangle.\n
            padding - additional spaces before values.
            """

            self.value = value
            self.edges = edges
            self.sides = sides
            self.padding = padding

        def get(self) -> str:
            """
            Return the box as a string.
            """
            max_len = len(max(self.value.split("\n"), key=len))

            box = f"{self.edges[0]}{self.sides[0]*(max_len + (self.padding * 2))}{self.edges[1]}\n"
            for i in self.value.split("\n"):
                box += f"{self.sides[1]}{" "*self.padding}{i.center(max_len)}{" "*self.padding}{self.sides[1]}\n"

            box += f"{self.edges[2]}{self.sides[0]*(max_len + (self.padding * 2))}{self.edges[3]}"

            return box
        
        def display(self) -> None:
            """
            Display the box.
            """
            cprint(self.get())

class Table:
    def __init__(self, values: list[str], connect: str = "+", sides: list[str] = ["-", "|", "="], padding: int = 1) -> None:
        """
        values  - an array of array each with a tuple of 2 bools and an array, the first boolean is a flag for continues the second is a flag for a break, the array is the row structure all the array should be the same length or 1 in which case only one boolean should be present, the flag for break. (Eg. values=[[(True, True), ["TITLE"]], [(False, True), ["1","row 1, column 0", "row 1, column 1", "row 1, column 2"]], [(False, True), ["1","row 2, column 0", "row 2, column 1", "row 2, column 2"]]] )\n
        sides   - the strings for the sides.\n
        connect - the string for the connections.\n
        padding - additional spaces before values.
        """

        for i in values:
            if len(i[1]) != len(max(values[1], key=len)) and len(i[1]) != 1:
                raise ValueError('Lengths of all values should be same or 1.')

        self.table = ""
        self.values = values
        self.connect = connect
        self.sides = sides
        self.padding = " " * padding
        self.length = 0
        for i in values:
            if len(i[1]) > self.length: self.length = len(i[1])
        
    def get(self) -> str:
        """
        Return the table as a list.
        """
        max_len = 0
            
        for i in self.values:
            length = len(max(i[1], key=len))
            if length > max_len:
                max_len = length
            else:
                length = max_len

        max_len += len(self.padding * 2)
            
        for c, i in enumerate(self.values):
            n_cont = self.values[c + 1][0][0] if c < len(self.values) - 1 else True
            br = self.values[c + 1][0][1] if c < len(self.values) - 1 else True

            self.table += self.connect if c == 0 else self.sides[1]

            if len(i[1]) != 1:
                cont = i[0][0]

                if cont:
                    self.table += f"{self.sides[0] * (max_len)}{self.connect if c == 0 else self.sides[1]}\n{self.sides[1]}" if c == 0 else ""

                else:
                    self.table += f"{self.sides[0] * (max_len)}{self.connect if c == 0 else self.sides[1]}\n{self.sides[1]}" if c == 0 else ""
                    
                for value in i[1]:
                    if cont:
                        self.table += f"{self.padding}{str(value).center(length)}{self.padding} "

                    else:
                        self.table += f"{self.padding}{str(value).center(length)}{self.padding}{self.sides[1]}"
            
                self.table = self.table[:-1]
                if br:
                    if not n_cont:
                        self.table += f"{self.sides[1]}\n{self.connect if c == 0 or c == len(self.values) - 1 else self.sides[1]}{f"{(self.sides[0] if c == 0 or c == len(self.values) - 1 else self.sides[2]) * (max_len)}{self.connect}" * self.length}"
                        self.table = self.table[:-1]
                        self.table += f"{self.connect if c == 0 or c == len(self.values) - 1 else self.sides[1]}\n"

                    else:
                        self.table += f"{self.sides[1]}\n{self.connect if c == 0 or c == len(self.values) - 1 else self.sides[1]}{(self.sides[0] if c == 0 or c == len(self.values) - 1 else self.sides[2]) * (max_len * self.length + self.length - 1)}{self.connect if c == 0 or c == len(self.values) - 1 else self.sides[1]}\n"

                else:
                    self.table += f"{self.sides[1]}\n"

            else:
                full_len = max_len * self.length

                self.table += f"{self.sides[0] * (full_len + self.length - 1)}{self.connect if c == 0 else self.sides[1]}\n{self.sides[1]}" if c == 0 else ""
 
                self.table += f"{self.padding}{str(i[1][0]).center(full_len)}{self.padding}"
            
                if br:
                    if not n_cont:
                        self.table += f"{self.sides[1]}\n{self.connect if c == 0 or c == full_len - 1 else self.sides[1]}{f"{(self.sides[0] if c == 0 or c == full_len - 1 else self.sides[2]) * (max_len)}{self.connect}" * self.length}"
                        self.table = self.table[:-1]
                        self.table += f"{self.connect if c == 0 or c == full_len - 1 else self.sides[1]}\n"

                    else:
                        self.table += f"{self.sides[1]}\n{self.connect if c == 0 or c == full_len - 1 else self.sides[1]}{(self.sides[0] if c == 0 or c == full_len - 1 else self.sides[2]) * (full_len + self.length - 1)}{self.connect if c == 0 or c == full_len - 1 else self.sides[1]}\n"

                else:
                    self.table += f"{self.sides[1]}\n"


        return self.table
    
    def display(self):
        """
        Display the table.
        """
        cprint(self.get())



class Ansi:
    def __init__(self) -> None:
        pass

    class Color:
        def __init__(self) -> None:
            pass

        BLACK = "\033[0;30m"
        @staticmethod
        def black(text: str) -> str: return f"\033[0;30m{text}\033[0m"

        RED = "\033[0;31m"
        @staticmethod
        def red(text: str) -> str: return f"\033[0;31m{text}\033[0m"  

        GREEN = "\033[0;32m"
        @staticmethod
        def green(text: str) -> str: return f"\033[0;32m{text}\033[0m"

        BROWN = "\033[0;33m"
        @staticmethod
        def brown(text: str) -> str: return f"\033[0;33m{text}\033[0m"

        BLUE = "\033[0;34m"
        @staticmethod
        def blue(text: str) -> str: return f"\033[0;34m{text}\033[0m"

        PURPLE = "\033[0;35m"
        @staticmethod
        def purple(text: str) -> str: return f"\033[0;35m{text}\033[0m"

        CYAN = "\033[0;36m"
        @staticmethod
        def cyan(text: str) -> str: return f"\033[0;36m{text}\033[0m"

        LIGHT_GRAY = "\033[0;37m"
        @staticmethod
        def light_gray(text: str) -> str: return f"\033[0;37m{text}\033[0m"

        GRAY = "\033[1;30m"
        @staticmethod
        def gray(text: str) -> str: return f"\033[1;30m{text}\033[0m"

        LIGHT_RED = "\033[1;31m"
        @staticmethod
        def light_red(text: str) -> str: return f"\033[1;31m{text}\033[0m"

        LIGHT_GREEN = "\033[1;32m"
        @staticmethod
        def light_green(text: str) -> str: return f"\033[1;32m{text}\033[0m"

        YELLOW = "\033[0;33m"
        @staticmethod
        def yellow(text: str) -> str: return f"\033[1;33m{text}\033[0m"

        LIGHT_BLUE = "\033[1;34m"
        @staticmethod
        def light_blue(text: str) -> str: return f"\033[1;34m{text}\033[0m"

        LIGHT_PURPLE = "\033[1;35m"
        @staticmethod
        def light_purple(text: str) -> str: return f"\033[1;35m{text}\033[0m"

        LIGHT_CYAN = "\033[1;36m"
        @staticmethod
        def light_cyan(text: str) -> str: return f"\033[1;36m{text}\033[0m"

        WHITE = "\033[0;37m"
        @staticmethod
        def white(text: str) -> str: return f"\033[0;37m{text}\033[0m"

        LIGHT_WHITE = "\033[1;37m"
        @staticmethod
        def light_white(text: str) -> str: return f"\033[1;37m{text}\033[0m"
        
        @staticmethod
        def rainbow(text: str, bold: bool = False) -> str:
            colors = [f"\033[{'1' if bold else '0'};3" + "{}m{{}}\033[0m".format(n) for n in range(1,7)]
            rainbow = itertools.cycle(colors)
            letters = [next(rainbow).format(l) for l in text]
            return "".join(letters)
        
        @staticmethod
        def rgb(r, g, b) -> str: return f"\033[38;2;{r};{g};{b}m"

    class BgColor:
        def __init__(self) -> None:
            pass
        
        BLACK = "\033[0;40m"
        @staticmethod
        def black(text: str) -> str: return f"\033[0;40m{text}\033[0m"

        RED = "\033[0;41m"
        @staticmethod
        def red(text: str) -> str: return f"\033[0;41m{text}\033[0m"  

        GREEN = "\033[0;42m"
        @staticmethod
        def green(text: str) -> str: return f"\033[0;42m{text}\033[0m"

        BROWN = "\033[0;43m"
        @staticmethod
        def brown(text: str) -> str: return f"\033[0;43m{text}\033[0m"

        BLUE = "\033[0;44m"
        @staticmethod
        def blue(text: str) -> str: return f"\033[0;44m{text}\033[0m"

        PURPLE = "\033[0;45m"
        @staticmethod
        def purple(text: str) -> str: return f"\033[0;45m{text}\033[0m"

        CYAN = "\033[0;46m"
        @staticmethod
        def cyan(text: str) -> str: return f"\033[0;46m{text}\033[0m"

        LIGHT_GRAY = "\033[0;47m"
        @staticmethod
        def light_gray(text: str) -> str: return f"\033[0;47m{text}\033[0m"

        GRAY = "\033[1;40m"
        @staticmethod
        def gray(text: str) -> str: return f"\033[1;40m{text}\033[0m"

        LIGHT_RED = "\033[1;41m"
        @staticmethod
        def light_red(text: str) -> str: return f"\033[1;41m{text}\033[0m"

        LIGHT_GREEN = "\033[1;42m"
        @staticmethod
        def light_green(text: str) -> str: return f"\033[1;42m{text}\033[0m"

        YELLOW = "\033[0;43m"
        @staticmethod
        def yellow(text: str) -> str: return f"\033[1;43m{text}\033[0m"

        LIGHT_BLUE = "\033[1;44m"
        @staticmethod
        def light_blue(text: str) -> str: return f"\033[1;44m{text}\033[0m"

        LIGHT_PURPLE = "\033[1;45m"
        @staticmethod
        def light_purple(text: str) -> str: return f"\033[1;45m{text}\033[0m"

        LIGHT_CYAN = "\033[1;46m"
        @staticmethod
        def light_cyan(text: str) -> str: return f"\033[1;46m{text}\033[0m"

        WHITE = "\033[0;47m"
        @staticmethod
        def white(text: str) -> str: return f"\033[0;47m{text}\033[0m"

        LIGHT_WHITE = "\033[1;47m"
        @staticmethod
        def light_white(text: str) -> str: return f"\033[1;47m{text}\033[0m"

        @staticmethod
        def rainbow(text: str, bold: bool = False) -> str:
            colors = [f"\033[{'1' if bold else '0'};4" + "{}m{{}}\033[0m".format(n) for n in range(1,7)]
            rainbow = itertools.cycle(colors)
            letters = [next(rainbow).format(l) for l in text]
            return "".join(letters)
        
        @staticmethod
        def rgb(r, g, b) -> str: return f"\033[48;2;{r};{g};{b}m"

    BOLD = "\033[1m"
    @staticmethod
    def bold(text: str) -> str: return f"\033[1m{text}\033[0m"

    FAINT = "\033[2m"
    @staticmethod
    def faint(text: str) -> str: return f"\033[2m{text}\033[0m"
    
    ITALIC = "\033[3m"
    @staticmethod
    def italic(text: str) -> str: return f"\033[3m{text}\033[0m"

    UNDERLINE = "\033[4m"
    @staticmethod
    def underline(text: str) -> str: return f"\033[4m{text}\033[0m"

    BLINK = "\033[5m"
    @staticmethod
    def blink(text: str) -> str: return f"\033[5m{text}\033[0m"

    NEGATIVE = "\033[7m"
    @staticmethod
    def negative(text: str) -> str: return f"\033[7m{text}\033[0m"

    HIDDEN = "\033[8m"
    @staticmethod
    def hidden(text: str) -> str: return f"\033[8m{text}\033[0m"

    CROSSED = "\033[9m"
    @staticmethod
    def crossed(text: str) -> str: return f"\033[9m{text}\033[0m"

    END = "\033[0m"
    @staticmethod
    def end() -> None: print(f"\033[0m")

    BELL = "\033[G"
    @staticmethod
    def bell() -> None: print("\033[G", end="")

    @staticmethod
    def resize_win(w: int, h: int) -> None:
        print(f"\033[8;{w};{h}t", end="")
    
    class Cursor:
        def __init__(self) -> None:
            pass

        HIDE = "\033[?25l"
        @staticmethod
        def hide() -> None: print("\033[?25l", end="")

        SHOW = "\033[?25h"
        @staticmethod
        def show() -> None: print("\033[?25h", end="")

        HOME = "\033[H"
        @staticmethod
        def home() -> None: print("\033[H", end="")

        UP = "\033[A"
        @staticmethod
        def up(lines: int = 1) -> None: print(f"\033[{lines}A", end="")

        DOWN = "\033[B"
        @staticmethod
        def down(lines: int = 1) -> None: print(f"\033[{lines}B", end="")

        LEFT = "\033[D"
        def left(char: int = 1) -> None: print(f"\033[{char}D", end="")

        RIGHT = "\033[C"
        @staticmethod
        def right(char: int = 1) -> None: print(f"\033[{char}C", end="")

        UP_B = "\033[F"
        @staticmethod
        def up_b(lines: int = 1) -> None: print(f"\033[{lines}F", end="")

        DOWN_B = "\033[E"
        @staticmethod
        def down_b(lines: int = 1) -> None: print(f"\033[{lines}E", end="")

        MOVE_TO = "\033[G"
        @staticmethod
        def move_to(line: int) -> None: print(f"\033[{line}G", end="")

        SAVE = "\033[s"
        @staticmethod
        def save() -> None: print("\033[s", end="")

        RESTORE = "\033[u"
        @staticmethod
        def restore() -> None: print("\033[u", end="")

    class Erase:
        def __init__(self) -> None:
            pass
        
        CURSOR_END = "\033[J"
        @staticmethod
        def cursor_end() -> None: print("\033[J", end="")

        CURSOR_BEGIN = "\033[1J"
        @staticmethod
        def cursor_begin() -> None: print("\033[1J", end="")

        SCREEN = "\033[H\033[2J"
        @staticmethod
        def screen() -> None: print("\033[H\033[2J", end="")

        LINE = "\033[K"
        @staticmethod
        def line() -> None: print("\033[K", end="")

class TextObfTransition:
    def __init__(self, old: str, new: str, change: int = 4, time: float = 0.15, original_time: float = 0.45, input: bool = False) -> None:
        """
        old           - the string it will be transitioning from.\n
        new           - the string it will be transitioning to.\n
        change        - the amount of times (+ len(new)) the text will change.\n
        time          - delay between text changes.\n
        original_time - the time for which the original string will stay showing.\n
        input         - provide an empty input prompt (forgot why i added this but am scared to remove)
        """
        self.old = old
        self.new = new
        self.change = change
        self.time = time
        self.original_time = original_time
        self.input = input

    def display(self) -> None:
        """
        Display the transition.
        """
        pprint(self.old)
        if self.input: input(); Ansi.Cursor.up()
        else: time.sleep(self.original_time)

        for i in range(len(self.new)):
            if i <= len(self.new):
                pprint(self.new[:i] + "".join([chr(random.randrange(97, 122)) for _ in range(len(self.old) - i)]))
                time.sleep(self.time)

        cprint(self.new)
        flush_input()

class ProgressBar:
    def __init__(self, total: int, prepend: str = "", append: str = "", type: str = "p", full: str = "█", empty: str = " ", border: str = "|", auto_start: bool = True, display_complete: bool = True) -> None:
        """
        total   - the amount of next calls required to complete the bar.\n
        prepend - the string before the progress bar.\n
        append  - the string after the progress bar.\n
        type    - the type of bar ProgressBar.PERCENT for percents (x%) or ProgressBar.NUMBER for numbers ([x/x]).\n
        full    - the character displayed at the reached part of the bar.\n
        empty   - the character displayed at the not reached part of the bar.\n
        border  - the border for the bar.
        """
        
        self.total = total
        self.full = full
        self.empty = empty
        self.border = border
        self.places = 100
        self.prepend = prepend
        self.append = append
        self.current = 0
        self.type = type
        self.bar = ""
        self.p = display_complete
        self.times = []
        self.start_t = 0
        self.end_t = 0
        self.auto_start = auto_start

        if auto_start:
            self._start()

    PERCENT = "p"
    NUMBER = "n"

    def _start(self) -> None:
        self.start_t = time.perf_counter()
        fill = 0
        if self.type == "p":
            percent = 0
            self.bar = f"{self.prepend}{self.border}{self.full * (fill)}{self.empty * (self.places - fill)}{self.border}{f" {percent}%" if self.p else ""}{self.append}"

        elif self.type == "n":
            self.bar = f"{self.prepend}{self.border}{self.full * (fill)}{self.empty * (self.places - fill)}{self.border}{f" [{self.current}/{self.total}]" if self.p else ""}{self.append}"

        pprint(self.bar)

    def start(self):
        """
        **Only call this if auto_start is off (on by default), it will do nothing otherwise.**
        Print the initial 0% or 0/x bar.
        """
        
        if not self.auto_start:
            self._start()

    def set_append(self, string: str) -> None:
        self.append = string

    def set_prepend(self, string: str) -> None:
        self.prepend = string

    def next(self) -> int:
        """
        Update the bar.\n
        This function should be called 'total' times to complete the bar.
        """
        self.end_t = time.perf_counter()
        self.times.append(self.end_t - self.start_t)
        self.start_t = time.perf_counter()
        self.current += 1
        fill = round(self.current / self.total * self.places)
        if self.type == "p":
            percent = round(self.current / self.total * 100)
            self.bar = f"{self.prepend}{self.border}{self.full * (fill)}{self.empty * (self.places - fill)}{self.border}{f" {percent}%" if self.p else ""}{self.append}"
            pprint(self.bar)
            if self.current == self.total:
                self._end()
            return percent

        elif self.type == "n":
            self.bar = f"{self.prepend}{self.border}{self.full * (fill)}{self.empty * (self.places - fill)}{self.border}{f" [{self.current}/{self.total}]" if self.p else ""}{self.append}"
            pprint(self.bar)
            if self.current == self.total:
                self._end()
            return self.current
        
    def eta(self, float: bool = False, unknown: str = "?") -> str:
        """
        Estimate the time of end for the progress bar.
        """
        if len(self.times) > 0:
            if float:
                return statistics.mean(self.times) * (self.total - self.current)
            
            return round(statistics.mean(self.times) * (self.total - self.current))
        
        else:
            return unknown
        
    def _end(self) -> None:
        """
        Print the bar so it stays when pprint is called again.\n
        **THIS FUNCTION SHOULD ONLY BE CALLED IF THE BAR DOESN'T REACH 100%.**
        """
        cprint(self.bar)
        flush_input()
        
    def get(self) -> str:
        """
        Return the bar as a string.
        """
        return self.bar

        
class Loader:
    def __init__(self, type: str, index: int = 0, sleep: float = 0.1, seq: list[str] = None) -> None:
        """
        type  - 'Loader.SPINNER' for spinner, 'Loader.DOTS' for dots.\n
        index - specify an index from 0 - 3 for which spinner to use or 0 - 4 for which dot sequence to use.\n
        sleep - time the loader will wait before displaying the next frame.\n
        seq   - sequence for loader leave as None to use type. (Eg. SPINNER 0 sequence: ["⠋", "⠙", "⠴", "⠦"]).
        """
        self.type = type
        self.index = index
        self.c = 0
        self.stop_flag = False
        self.sleep = sleep

        if type == self.SPINNER:
            self.seq = [
                ["⠋", "⠙", "⠴", "⠦"],
                ["|", "/", "-", "\\"],
                ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
                ["⠋", "⠙", "⠚", "⠞", "⠖", "⠦", "⠴", "⠲", "⠳", "⠓"],
            ][self.index]

        if type == self.DOTS:
            self.seq = [
                [".  ", ".. ", "...", ".. "],
                ["---", "--.", "-..", "...", ".._", ".__", "___", "__.", "_..", "...", "..-", ".--"],
                ["---", "--.", "-..", "...", "..-", ".--"],
                ["▁▃█▃▁", "▃█▃▁▃", "█▃▁▃█", "▃▁▃█▃"],
                ["---", "-.-", "..."]
                ][self.index]

        if seq:
            self.seq = seq
        
    SPINNER = "spinner"
    DOTS = "dots"

    def next(self) -> None:
        "Go to the next iteration of the spinner."
        if self.c > len(self.seq) - 1:
            self.c = 0

        pprint(self.seq[self.c])

        self.c += 1

    def end(self):
        """
        Delete the spinner.
        """
        pprint("")

    def get_next(self) -> str:
        """
        Return next iteration as string.
        """
        if self.c > len(self.seq) - 1:
            self.c = 0

        self.c += 1

        return self.seq[self.c - 1]


    def _start(self) -> None:
        while not self.stop_flag:
            self.next()
            time.sleep(self.sleep)
        
        pprint("")

    def start(self) -> None:
        """
        Start the spinner in a thread
        """
        threading.Thread(target=self._start).start()

    def stop(self) -> None:
        """
        Stop the spinner and call end (to stop without calling end run semi_stop).
        """
        self.stop_flag = True
        self.end()
        flush_input()

    def semi_stop(self) -> None:
        """
        Stop the spinner and **don't** call end.
        """
        self.stop_flag = True

class Animate:
    def __init__(self, frames: list) -> None:
        """
        frames - list of strings each representing a frame of animation.
        """
        
        self.frames = frames
        self.index = -1
        self.stop = False

    def _start(self, delay: float = 0.1) -> None:
        while not self.stop:
            pprint(self.next())
            time.sleep(delay)

    def start(self, delay: float = 0.2) -> None:
        """
        Start the animation in a thread.
        """
        threading.Thread(target=self._start, args=(delay,)).start()

    def next(self) -> str:
        """
        Go to the next iteration of the animation and return frame as string.
        """
        self.index = self.index + 1 if self.index < len(self.frames) - 1 else 0
        return self.frames[self.index]

    def end(self, lock = False) -> None:
        """
        Stop the animation.\n
        lock - if true the animation will freeze at the end frame else it will get removed at end.
        """
        self.stop = True
        if lock: cprint(self.next())
        else: pprint("")
        flush_input-8

    def once(self, delay: float = 0.2, lock = False) -> None:
        """
        Display the animation once.\n
        lock - if true the animation will freeze at the end frame else it will get removed at end.
        """
        last = ""
        for frame in self.frames:
            pprint(frame)
            last = frame
            time.sleep(delay)

        if lock: cprint(last)
        else: pprint("")
        flush_input()

class Layout:   
    def __init__(self, width: int, height: int) -> None:
            """
            width  - the width of the screen.\n
            height - the height of the screen.
            """
            self.width = width
            self.height = height
            self.layout = []
            self.tot_lines = 0

    def _overwrite(self, value: str, line: int) -> None:
        if line == -1:
            line = self.tot_lines + 1

        if line > self.tot_lines < self.height - 1:
            for _ in range(line - self.tot_lines - 1): self.layout.append("")
            self.layout.append(value)

        elif line < self.height - 1:
            self.layout[line] = value

        self.tot_lines = len(self.layout) - 1
            
    def _get(self, line: int) -> str:
        if line == -1:
            line = self.tot_lines + 1

        try: return self.layout[line] 
        except IndexError: return ""
    
    def anchor_left(self, value: str, line: int | None = -1) -> None:
        """
        Anchor text to left.
        """
        self._overwrite(f"{self._get(line)}{" " * (self.width - len(self._get(line)) - len(value))}{value}", line)
        
    def anchor_right(self, value: str, line: int | None = -1) -> None:
        """
        Anchor text to right.
        """
        self._overwrite(f"{value}{self._get(line)}", line)

    def raw(self, value: str, line: int | None = -1) -> None:
        """
        Add text raw.
        """
        if len(f"{self._get(line)}{value}") <= self.width:
            self._overwrite(f"{self._get(line)}{value}", line)

        else:
            raise ValueError(f"Line is {len(f"{self._get(-1)}{value}")} characters long when max length is {self.width}.")

    def get(self) -> str:
        """
        Get the layout as a string.
        """
        return "\n".join(self.layout)
    
    def display(self) -> None:
        """
        Display the layout.
        """
        cprint(self.get())

class ImageToText:
    def __init__(self) -> None:
        pass

    class Color:
        def __init__(self, path: str) -> None:
            """
            path - path to image.
            """
            self.path = path

        def _get(self, im: Image) -> str:
            img = ""
            for y in range(im.height):
                for x in range(im.width):
                    img += (Ansi.rgb_bg(*im.getpixel((x, y))) + " " * 2 + Ansi.END)
                
                img += "\n"
            
            return img[:-1]
        
        def get(self) -> str:
            """
            Returns image as string.
            """
            return self._get(Image.open(self.path).convert("RGB"))

        def display(self) -> None:
            """
            Display image.
            """
            cprint(self.get())
        
    class ColorEmoji:
        def __init__(self, path: str) -> None:
            """
            path - path to image.
            """
            self.path = path
        
        def _get(self, im) -> str:
            img = ""
            for y in range(im.height):
                for x in range(im.width):
                    pixel_rgb = 765 - sum(im.getpixel((x, y)))

                    if pixel_rgb > 690:
                        img += "⬜"

                    elif pixel_rgb > 600:
                        img += "🟨"

                    elif pixel_rgb > 500:
                        img += "🟪"

                    elif pixel_rgb > 450:
                        img += "🟧"

                    elif pixel_rgb > 350:
                        img += "🟦"

                    elif pixel_rgb > 300:
                        img += "🟩"

                    elif pixel_rgb > 250:
                        img += "🟥"

                    elif pixel_rgb > 200:
                        img += "🟫"

                    else:
                        img += "⬛"
                                
                img += "\n"
            
            return img[:-1]
        
        def get(self) -> str:
            """
            Returns image as string.
            """
            return self._get(Image.open(self.path).convert("RGB"))

        def display(self) -> None:
            """
            Returns image as string.
            """
            cprint(self.get())

    class Monochrome:
        def __init__(self, path: str, density: dict = {'Ñ': 255, '@': 245, '#': 235, 'W': 225, '$': 215, '9': 205, '8': 195, '7': 185, '6': 175, '5': 165, '4': 155, '3': 145, '2': 135, '1': 125, '0': 115, '?': 105, '!': 95, 'a': 85, 'b': 75, 'c': 65, ';': 55, ':': 50, '+': 45, '=': 40, '-': 35, ',': 25, '.': 15, '_': 5}) -> None:
            """
            path    - path to image.\n
            density - the density for the image.
            """
            self.path = path
            self.density = density
        def _get(self, im: Image) -> str:
            img = ""
            for y in range(im.height):
                for x in range(im.width):
                    pixel = im.getpixel((x, y))
                    
                    res_key, _ = min(self.density.items(), key=lambda i: abs(pixel - i[1]))
                    img += f" {res_key} "

                img += "\n"

            return img[:-1]
        
        def get(self) -> str:
            """
            Returns image as string.
            """
            return self._get(Image.open(self.path).convert("L"))
        
        def display(self) -> None:
            """
            Returns image as string.
            """
            cprint(self.get())

class VideoToText:
    def __init__(self) -> None:
        pass

    class Color:
        def __init__(self, path: str) -> None:
            """
            path - path to video file
            """
            self.path = path
            self.frames = []
        
        def get(self, progress = True) -> list[str]:
            """
            Return the frames converted to text as list.
            """
            cap = cv2.VideoCapture(self.path)

            success = 1

            if progress:
                p = ProgressBar(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
                p.start()
        
            while success:
                success, im = cap.read()

                if not success:
                    break
                
                im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                
                frame = Image.fromarray(im)
                frame = ImageToText.Color("")._get(frame)

                self.frames.append(frame)
                if progress:
                    p.next()
                cv2.waitKey(0)

            return self.frames
        
        def display(self, progress: bool = True, lock: bool = True) -> None:
            """
            Display the video.
            """
            Animate(self.get(progress)).once(0, lock)

        def _save(self, name: str, progress: bool = False) -> None:
            if self.frames:
                frames = self.frames

            else:
                t = threading.Thread(target=self.get, args=(progress,))
                t.start()
                frames = t.join()

            if name not in dir(self):
                setattr(self, name, frames)

            else:
                raise ValueError(f"'{name}' already exists.")
            
        def save(self, name: str, progress: bool = False, background: bool = True) -> None:
            """
            Save the video as an attribute in the instance.\n
            name       - what to save the video as (will be used in load).\n
            progress   - show the progress bar.\n
            background - run it in another thread so it doesn't interfere with other code.
            """

            if background: 
                threading.Thread(target=self._save, args=(name, progress)).start()

            else:
                if self.frames:
                    frames = self.frames

                else:
                    frames = self.get()

                if name not in dir(self):
                    setattr(self, name, frames)

                else:
                    raise ValueError(f"'{name}' already exists.")
        
        def is_saved(self, name: str) -> bool:
            """
            Returns True if the video with that name has been saved.
            """
            try:
                getattr(self, name)
                return True
            except AttributeError:
                    return False

        def load(self, name: str) -> None:
            """
            Load and display a saved video. 
            """

            try:
                Animate(getattr(self, name)).once()
            except AttributeError:
                raise ValueError(f"No video saved with the name '{name}'.")

        def get_load(self, name: str) -> list[str]:
            """
            Load and return as list the saved video.
            """
            try:
                return getattr(self, name)
            except AttributeError:
                    raise ValueError(f"No video saved with the name '{name}'.")

    class ColorEmoji:
        def __init__(self, path: str) -> None:
            """
            path - path to video file
            """
            self.path = path
            self.frames = []

        def get(self, progress = True) -> list[str]:
            """
            Return the frames converted to text as list.
            """
            cap = cv2.VideoCapture(self.path)

            success = 1

            if progress:
                p = ProgressBar(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
                p.start()
        
            while success:
                success, im = cap.read()

                if not success:
                    break

                im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

                frame = Image.fromarray(im)
                frame = ImageToText.ColorEmoji("")._get(frame)
                self.frames.append(frame)
                if progress:
                    p.next()
                cv2.waitKey(0)

            return self.frames

        def display(self, progress: bool = True) -> None:
            """
            Display the video.
            """
            Animate(self.get(progress)).once()

        def _save(self, name: str, progress: bool = False) -> None:
            if self.frames:
                frames = self.frames

            else:
                t = threading.Thread(target=self.get, args=(progress,))
                t.start()
                frames = t.join()

            if name not in dir(self):
                setattr(self, name, frames)

            else:
                raise ValueError(f"'{name}' already exists.")
            
        def save(self, name: str, progress: bool = False, background: bool = True) -> None:
            """
            Save the video as an attribute in the instance.\n
            name       - what to save the video as (will be used in load).\n
            progress   - show the progress bar.\n
            background - run it in another thread so it doesn't interfere with other code.
            """

            if background: 
                threading.Thread(target=self._save, args=(name, progress)).start()

            else:
                if self.frames:
                    frames = self.frames

                else:
                    frames = self.get()

                if name not in dir(self):
                    setattr(self, name, frames)

                else:
                    raise ValueError(f"'{name}' already exists.")
        
        def is_saved(self, name: str) -> bool:
            """
            Returns True if the video with that name has been saved.
            """
            try:
                getattr(self, name)
                return True
            except AttributeError:
                    return False

        def load(self, name: str) -> None:
            """
            Load and display a saved video. 
            """

            try:
                Animate(getattr(self, name)).once()
            except AttributeError:
                raise ValueError(f"No video saved with the name '{name}'.")

        def get_load(self, name: str) -> list[str]:
            """
            Load and return as list the saved video.
            """
            try:
                return getattr(self, name)
            except AttributeError:
                    raise ValueError(f"No video saved with the name '{name}'.")

    class Monochrome:
        def __init__(self, path: str) -> None:
            """
            path - path to video file
            """
            self.path = path
            self.frames = []
        
        def get(self, progress = True) -> list[str]:
            """
            Return the frames converted to text as list.
            """
            cap = cv2.VideoCapture(self.path)

            success = 1

            if progress:
                p = ProgressBar(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
                p.start()
        
            while success:
                success, im = cap.read()

                if not success:
                    break

                im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

                frame = Image.fromarray(im)
                frame = ImageToText.Monochrome("")._get(frame)
                self.frames.append(frame)
                if progress:
                    p.next()
                cv2.waitKey(0)

            return self.frames
        
        def display(self, progress: bool = True) -> None:
            """
            Display the video.
            """
            Animate(self.get(progress)).once()

        def _save(self, name: str, progress: bool = False) -> None:
            if self.frames:
                frames = self.frames

            else:
                t = threading.Thread(target=self.get, args=(progress,))
                t.start()
                frames = t.join()

            if name not in dir(self):
                setattr(self, name, frames)

            else:
                raise ValueError(f"'{name}' already exists.")
            
        def save(self, name: str, progress: bool = False, background: bool = True) -> None:
            """
            Save the video as an attribute in the instance.\n
            name       - what to save the video as (will be used in load).\n
            progress   - show the progress bar.\n
            background - run it in another thread so it doesn't interfere with other code.
            """

            if background: 
                threading.Thread(target=self._save, args=(name, progress)).start()

            else:
                if self.frames:
                    frames = self.frames

                else:
                    frames = self.get()

                if name not in dir(self):
                    setattr(self, name, frames)

                else:
                    raise ValueError(f"'{name}' already exists.")
        
        def is_saved(self, name: str) -> bool:
            """
            Returns True if the video with that name has been saved.
            """
            try:
                getattr(self, name)
                return True
            except AttributeError:
                    return False

        def load(self, name: str) -> None:
            """
            Load and display a saved video. 
            """

            try:
                Animate(getattr(self, name)).once()
            except AttributeError:
                raise ValueError(f"No video saved with the name '{name}'.")

        def get_load(self, name: str) -> list[str]:
            """
            Load and return as list the saved video.
            """
            try:
                return getattr(self, name)
            except AttributeError:
                    raise ValueError(f"No video saved with the name '{name}'.")
            
class UI:
    def __init__(self, color: tuple[int, int, int], size: tuple[int, int], darker: int = 30, bg_char: str = " ", spacing: int = 1) -> None:
        """
        color   - rgb values a tuple of (r, g, b)\n
        size    - a tuple of (width, height)\n
        darker  - the percentage that the border will be darker by.\n
        bg_char - the character(s) used for the background.\n
        spacing - the spacing between columns.
        """
        flush_input()
        self.color = color
        self.dark_mul = darker/100
        self.dark_color = (int(self.dark_mul * color[0]), int(self.dark_mul * color[1]), int(self.dark_mul * color[2]))
        self.w, self.h = size
        self.h += 1
        self.w += 1
        self.true_width = size[0]
        self.spacing = " " * spacing
        self.bg_char = bg_char * (spacing * 2)
        self.original_bg_char = bg_char
        self.ui: list = [f"{Ansi.rgb_bg(*color)}{self.bg_char}{Ansi.END}" * (self.w - 1)]
        self.ui += [f"{Ansi.rgb_bg(*color)}{self.bg_char}{Ansi.END}" * (self.w - 1) + f"{Ansi.rgb_bg(*self.dark_color)}{self.bg_char}{Ansi.END}"] * (self.h)
        self.ui = self.ui[:-1]
        self.ui[-1] = bg_char * 2 + (f"{Ansi.rgb_bg(*self.dark_color)}{self.bg_char}{Ansi.END}" * (self.w - 1))
        self.cline = -1
        self.isrunning = True
        self.inter = []
        self.inter_pos = []
        self.sel_inter = 0
        self.stopped = False

    def display(self, async_=False) -> None:
        """
        Display the UI.\n
        This will also start the interactive object handler if there are any interactive objects present so you have to use stop() to stop the UI display.
        """
        self.update()
        if self.inter: 
            self.t = threading.Thread(target=self._inter_handler)
            self.t.start()
            if not async_:
                self.wait()
        else: self.stop()

    def is_stopped(self) -> bool:
        return self.stopped
    
    def wait(self) -> None:
        self.t.join()

    def _stop(self) -> None:
        self.isrunning = False
        if self.t is not threading.current_thread():
            self.t.join()
            cprint(self.get())
            self.stopped = True
        
        flush_input()

    def stop(self) -> None:
        """
        Stops the UI
        """

        threading.Thread(target=self._stop).start()

    def update(self) -> None:
        """
        Updates the display.
        """
        self.update_inter()
        pprint(self.get())

    def get(self) -> str:
        """
        Return the UI as a string.
        """

        return "\n".join(self.ui)
    
    def title(self, text: str, flf_font_path: str) -> None:
        """
        Add a title with the figlet font specified at the top center of the screen.
        """
        for line, text in enumerate(Figlet(flf_font_path).get(text, width=self.w).split("\n")):
            self.center(text, line + 1)

    def blank(self) -> None:
        """
        Creates a blank line.
        """

        self.cline += 1

    def interaction(self, *values: tuple[str, str, int, Callable, Iterable[Any]]) -> None:
        """
        values - a tuple of: text: str, sel_text: str, line: int, func: Callable, args: Iterable[Any].\n
            text     - the text that will be displayed when the interaction isn't selected.\n
            sel_text - the text that will be displayed when the interaction is selected.\n
            line     - the line that the interaction will be displayed on.\n
            func     - the function that will be called when the interaction is selected.\n
            args     - any iterable of args for the function.
        """
        for text, sel_text, line, func, args in values:
            self.inter.append((func, args, text, sel_text, line))

    def _inter_handler(self):
        flush_input()
        while True:
            if not self.isrunning:
                return
            
            if keyboard.is_pressed("DOWN ARROW"):
                if self.sel_inter < len(self.inter) - 1:
                    self.sel_inter += 1

                else:
                    self.sel_inter = 0

                self.update()
                time.sleep(0.2)

            elif keyboard.is_pressed("UP ARROW"):
                if self.sel_inter > 0:
                    self.sel_inter -= 1

                else:
                    self.sel_inter = len(self.inter) - 1

                self.update()
                time.sleep(0.2)

            elif keyboard.is_pressed("ENTER"):
                self.inter[self.sel_inter][0](*self.inter[self.sel_inter][1])
                self.update()
                time.sleep(0.4)

    def update_inter(self) -> None:
        for c, inter in enumerate(self.inter):
            if c == self.sel_inter:
                self.raw(inter[3], inter[4])
                    
            else:
                self.raw(inter[2], inter[4])

    def get_pad(self, text: str, pad: int) -> str:
        return " " * pad + text

    def next_line(self) -> int:
        return self.cline + 1
    
    def get_line(self, line: int, raw = False) -> str:
        return self.ui[line] if raw else self._ansi_escape(self.ui[line])
    
    def get_bottom(self) -> int:
        return self.h - 3

    def center(self, text: str, line: int = -1, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        if line == -1:
            self.line(text.center(self.true_width), color)

        else:
            self.raw(text.center(self.true_width), line, color)

    def get_center(self, text: str) -> str:
        return text.center(self.true_width)
    
    def get_add_left(self, text: str, line: int, padding: int = 0) -> str:
        original = self.get_line(line)
        return " " * padding + text + original
    
    def get_add_right(self, text: str, line: int, padding: int = 0) -> str:
        original = self.get_line(line)
        return original + text.rjust(self.true_width - padding - len(original))
    
    def right(self, text: str, padding: int) -> str:
        return text.rjust(self.true_width - padding)

    def pad(self, text: str, line: int, pad: int) -> str:
        self.raw(" " * pad + text, line)

    def add_left(self, text: str, line: int, padding: int = 0, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        original = self.get_line(line)
        self.raw(" " * padding + text + original, line, color)
    
    def add_right(self, text: str, line: int, padding: int = 0, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        original = self.get_line(line)
        self.raw(original + text.rjust(self.true_width - padding - len(original)), line, color)

    def right(self, text: str, line: int, padding: int, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        self.raw(text.rjust(self.true_width - padding), line, color)

    def bottom(self, text: str, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        self.raw(text, self.h - 3, color)

    def _ansi_escape(self, text: str) -> str:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub("", text)

    def line(self, text: str, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        """
        Write value to next line.
        """
        self.raw(text, self.cline + 1, color)

    def raw(self, text: str, line: int, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        """
        Write (and override) value on specified line
        """
        check_text = self._ansi_escape(text)

        if line < self.h - 1:
            if len(check_text) < self.w:
                if line == 0:
                    self.cline = line
                    self.ui[line] = f"{Ansi.rgb_bg(*self.color)}{Ansi.rgb(*color)}{self.spacing.join(text)}{self.original_bg_char * ((self.w * 2) - len(self.spacing.join(text)) - 2)}{Ansi.END}"

                else:
                    self.cline = line
                    self.ui[line] = f"{Ansi.rgb_bg(*self.color)}{Ansi.rgb(*color)}{self.spacing.join(text)}{self.original_bg_char * ((self.w * 2) - len(self.spacing.join(text)) - 2)}{Ansi.rgb_bg(*self.dark_color)}{self.bg_char}{Ansi.END}"

class FontError(Exception):...

class Figlet:
    def __init__(self, font_name: str, download: bool = True) -> None:
        """
        font_name - the font name (Eg. font_name="big.flf" or font_name="big")
        If download is True the program will try to download the font from 'figlet.org/fonts'.
        """
        if not font_name.endswith(".flf"): font_name += ".flf"

        self.font_name = font_name

        if download:
            if not os.path.exists(font_name):
                with open(font_name, "w+") as f:
                    f.write(subprocess.Popen(f'curl "http://www.figlet.org/fonts/{font_name}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.read().decode())

        with open(font_name, encoding="utf-8") as f:
            self.font = f.read()
        if self.font.startswith("<!DOCTYPE"):
            os.remove(font_name)
            raise FontError(f"No font named '{font_name}' could be found.")

        self.width = 0
    
    def _check_width(self, string: str, width: int) -> bool:
        if self.width + len(string.split("\n")[0]) > width:
            self.width = 0
            return False
        
        else:
            self.width += len(string.split("\n")[0])
            return True

    def _parse(self, text: str, indicator: str, space: str, padding: int, width: int) -> list[list[str]]:
        vars = self.font.split("\n")[0].split("flf2a")[1].split(" ")
        blank = vars[0]
        height = vars[1]

        for c, line in enumerate(self.font.split("\n")):
            if line.replace(blank, "").replace(indicator, "").replace(" ", "") == "" and indicator in line and blank in line:
                contents = self.font.split("\n")[c:]
                break

        chars_list: list[list[str]] = []
        char_line: list[str] = []

        for chr in text:
            chars: list[str] = []
            c = []

            for line in contents:
                if indicator * 2 in line:
                    c.append(space[0] * padding + line[1:-2])
                    chars.append("\n".join(c))
                    c = []

                else:
                    c.append(space[0] * padding + line[1:-1])

            char = chars[ord(chr) - 32]

            if char.replace(" ", "").replace(blank, "").replace("\n", "") == "":
                char_line.append("\n".join([space] * int(height)))
                if not self._check_width("\n".join([space] * int(height)), width):
                    chars_list.append(char_line)
                    char_line = []

            else:
                char_line.append(char.replace(blank, " "))
                if not self._check_width(char.replace(blank, " "), width):
                        chars_list.append(char_line)
                        char_line = []

        if char_line:
            chars_list.append(char_line)

        return chars_list
    
    def get(self, text: str, indicator: str = "@", space: str = " " * 3, padding: int = 0, width: int = 120) -> str:
        """
        Return text in a given figlet font wrapped to width.\n
        """
        lines = []
        try:
            parsed = self._parse(text, indicator, space, padding, width)
        except:
            raise FontError(f"The font file '{self.font_name}' seems to be corrupt.")

        for line in parsed:
            lines.append(nget(*line))
        
        return "\n".join(lines)
    
    def display(self, text: str, indicator: str = "@", space: str = " " * 3, padding: int = 0, width: int = 120) -> None:
        """
        Display the text.
        """
        cprint(self.get(text, indicator, space, padding, width))