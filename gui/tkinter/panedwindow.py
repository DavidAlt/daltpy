import tkinter as tk
from tkinter import ttk

# StackOverflow question on configuring: https://stackoverflow.com/questions/53675327/unknown-option-bad-command-on-configuring-ttk-panedwindow-and-panes

# setup the panedwindow
root = tk.Tk()
paned_w = ttk.Panedwindow(root, orient=tk.HORIZONTAL, width=300, height=300)
paned_w.pack(fill='both', expand=True)

# setup the panels
left_p = ttk.Label(paned_w, background='red')
right_p = ttk.Label(paned_w, background='yellow')
paned_w.add(left_p, weight=1, minsize=10)
paned_w.add(right_p, weight=3)

#paned_w.paneconfig(left_p, minsize=10)
#paned_w.paneconfig()


#paned_w.configure(width=600)
#print(paned_w.pane(left_p))
#print(paned_w.paneconfigure())

root.mainloop()