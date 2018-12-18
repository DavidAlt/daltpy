import logging
import tkinter as tk
from tkinter import ttk

logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('nested_paned_window')
log.setLevel(logging.DEBUG)


if __name__ == '__main__':
    master = tk.Tk()
    master.title = 'Nested Paned Windows'
    
    outer_panes = tk.PanedWindow(master)
    outer_panes.pack(fill=tk.BOTH, expand=1)

    right = tk.Label(outer_panes, text="right pane")
    inner_panes = tk.PanedWindow(outer_panes, orient=tk.VERTICAL)
    
    
    outer_panes.add(inner_panes)
    outer_panes.add(right)

    top = tk.Label(inner_panes, text="top pane")
    inner_panes.add(top)

    bottom = tk.Label(inner_panes, text="bottom pane")
    inner_panes.add(bottom)

    master.mainloop()