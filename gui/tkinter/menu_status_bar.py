import tkinter as tk
from tkinter import ttk

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('menu_sbar')
log.setLevel(logging.DEBUG)




class StatusBar(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.label.pack(fill=tk.X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()


def callback():
    log.info('')


def setup_menu(parent):
    # master menu
    menu = tk.Menu(parent)
    parent.config(menu=menu)

    # file menu
    filemenu = tk.Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="New", command=callback)
    filemenu.add_command(label="Open...", command=callback)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=callback)

    # help menu
    helpmenu = tk.Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="About...", command=callback)


def setup_toolbar(parent):
    toolbar = tk.Frame(parent)

    b = tk.Button(toolbar, text="new", width=6, command=callback)
    b.pack(side=tk.LEFT, padx=2, pady=2)

    b = tk.Button(toolbar, text="open", width=6, command=callback)
    b.pack(side=tk.LEFT, padx=2, pady=2)

    toolbar.pack(side=tk.TOP, fill=tk.X)


def setup_statusbar(parent):
    sbar = StatusBar(parent).pack(side=tk.BOTTOM, fill=tk.X)


if __name__ == '__main__':
    
    master = tk.Tk()
    master.wm_title('Menu and Status Bars')

    setup_menu(master)
    setup_toolbar(master)
    setup_statusbar(master)



    master.mainloop()        