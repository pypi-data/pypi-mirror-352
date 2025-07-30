import tkinter as tk
from typing import Callable, Generic, TypeVar
from .common import Box

T = TypeVar('T')


class TopEntry(Generic[T]):
    def __init__(self,
                 master: tk.TOP,
                 box: Box,
                 desc: T,
                 value: str,
                 callback: Callable[[T, str], bool]):
        self.top = tk.Toplevel(master)
        self.top.overrideredirect(True)
        self.top.bind("<FocusOut>", lambda e: self.top.destroy())
        self.top.geometry(str(box))
        self.desc = desc
        """descriptor"""
        self.variable = tk.StringVar(
            master=self.top,
            value=value)
        self.entry = tk.Entry(
            master=self.top,
            textvariable=self.variable,
            justify=tk.RIGHT
        )
        self.entry.bind("<Return>", self.__set_value)
        self.entry.bind("<Escape>", lambda e: self.top.destroy())
        self.entry.pack(
            fill=tk.X
        )
        self.cb = callback
        self.top.lift(master)
        self.entry.focus_set()

    def __set_value(self, _: tk.Event):
        try:
            self.cb(self.desc, self.variable.get())
            self.top.destroy()
        except ValueError as e:
            self.entry.configure(background="red")
            self.variable.set(str(e))


class TopOptionMenu:
    def __init__(self,
                 master: tk.TOP,
                 w: int, h: int,
                 x: int, y: int,
                 desc: list[str],
                 value: str,
                 values: list[str],
                 callback: Callable[[list[str], str], bool]):
        self.top = tk.Toplevel(master)
        self.top.overrideredirect(True)
        self.top.bind("<FocusOut>", lambda e: self.top.destroy())
        self.top.geometry(F"{w}x{h}+{x}+{y}")
        self.desc = desc
        """descriptor"""
        self.var = tk.StringVar(
            master=self.top,
            value=value)
        self.var.trace_add("write", self.__change_var)
        o_m = tk.OptionMenu(
            self.top,
            self.var,
            *values)
        # self.o_m.bind("<Return>", self.__set_value)
        o_m.bind("<Escape>", lambda e: self.top.destroy())
        o_m.pack(
            fill=tk.X
        )
        self.cb = callback
        self.top.lift(master)
        o_m.focus_set()

    def __change_var(self, *args):
        try:
            self.cb(self.desc, self.var.get())
            self.top.destroy()
        except ValueError as e:
            self.o_m.configure(background="red")
            self.var.set(str(e))

    def __set_value(self, e: tk.Event):
        try:
            self.cb(self.desc, self.var.get())
            self.top.destroy()
        except ValueError as e:
            self.o_m.configure(background="red")
            self.var.set(str(e))


class TopListBox:
    def __init__(self,
                 master: tk.TOP,
                 w: int, h: int,
                 x: int, y: int,
                 desc: list[str],
                 value: str,
                 values: list[str],
                 callback: Callable[[list[str], str], bool]):
        self.top = tk.Toplevel(master)
        self.top.overrideredirect(True)
        self.top.bind("<FocusOut>", lambda e: self.top.destroy())
        self.top.geometry(F"{w}x{h*min(10, len(values))}+{x}+{y+h}")
        self.desc = desc
        """descriptor"""
        self.values = values
        sc = tk.Scrollbar(
            master=self.top,
            orient=tk.VERTICAL)
        l_b = tk.Listbox(
            self.top,
            listvariable=tk.Variable(value=values),
            yscrollcommand=sc.set)
        sc.configure(command=l_b.yview)
        l_b.bind("<Double-Button-1>", self.__set_value)
        l_b.bind("<Return>", self.__set_value)
        l_b.bind("<Escape>", lambda e: self.top.destroy())
        l_b.pack(
            side=tk.LEFT,
            expand=1,
            fill=tk.BOTH)
        sc.pack(
            side=tk.RIGHT,
            fill=tk.Y)
        self.cb = callback
        self.top.lift(master)
        l_b.focus_set()

    def __set_value(self, e: tk.Event):
        try:
            w: tk.Listbox = e.widget
            if len(v := w.curselection()) == 1:
                self.cb(self.desc, self.values[v[0]])
                self.top.destroy()
            print(v)
        except ValueError as e:
            self.l_b.configure(background="red")
            self.var.set(str(e))
