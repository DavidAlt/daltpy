import tkinter as tk
from tkinter import ttk

# StackOverflow question on configuring: https://stackoverflow.com/questions/53675327/unknown-option-bad-command-on-configuring-ttk-panedwindow-and-panes

# setup the panedwindow
root = tk.Tk()
paned_w = ttk.PanedWindow(root, orient=tk.HORIZONTAL, width=300, height=300)
paned_w.pack(fill='both', expand=True)

# setup the panels
left_p = ttk.Label(paned_w, background='red')
right_p = ttk.Label(paned_w, background='yellow')
paned_w.add(left_p, weight=1)
paned_w.add(right_p, weight=3)

root.mainloop()