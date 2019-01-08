import os
import tkinter as tk
from tkinter import ttk

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('dir_browser')
log.setLevel(logging.DEBUG)


class DirBrowser(tk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setup_tree()


    def setup_tree(self):
        vsb = ttk.Scrollbar(self, orient="vertical")
        hsb = ttk.Scrollbar(self, orient="horizontal")

        tree = ttk.Treeview(self, columns=("fullpath", "type", "size"),
            displaycolumns="size", yscrollcommand=lambda f, l: self.autoscroll(vsb, f, l),
            xscrollcommand=lambda f, l: self.autoscroll(hsb, f, l))

        vsb['command'] = tree.yview
        hsb['command'] = tree.xview

        tree.heading("#0", text="Directory Structure", anchor='w')
        tree.heading("size", text="File Size", anchor='w')
        tree.column("size", stretch=0, width=100)

        self.populate_roots(tree)
        tree.bind('<<TreeviewOpen>>', self.update_tree)
        tree.bind('<<TreeviewSelect>>', self.on_select)
        #tree.bind('<Double-Button-1>', self.change_dir)
        tree.bind('<Button-3>', self.on_rclick)

        # Arrange the tree and its scrollbars in the toplevel
        tree.grid(column=0, row=0, sticky='nswe')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def populate_tree(self, tree, node):
        if tree.set(node, "type") != 'directory':
            return

        path = tree.set(node, "fullpath")
        tree.delete(*tree.get_children(node))

        parent = tree.parent(node)

        for p in os.listdir(path):
            ptype = None
            p = os.path.join(path, p).replace('\\', '/')
            if os.path.isdir(p): ptype = "directory"
            elif os.path.isfile(p): ptype = "file"

            fname = os.path.split(p)[1]
            id = tree.insert(node, "end", text=fname, values=[p, ptype])

            if ptype == 'directory':
                if fname not in ('.', '..'):
                    tree.insert(id, 0, text="dummy")
                    tree.item(id, text=fname)
            elif ptype == 'file':
                size = os.stat(p).st_size
                tree.set(id, "size", "%d bytes" % size)
        
        # Expand the root node
        tree.item(tree.get_children()[0], open=True)
        

    def populate_roots(self, tree):
        dir = os.path.abspath('.').replace('\\', '/')
        node = tree.insert('', 'end', text=dir, values=[dir, "directory"])
        self.populate_tree(tree, node)


    def update_tree(self, event):
        tree = event.widget
        self.populate_tree(tree, tree.focus())


    def on_rclick(self, event):
        tree = event.widget
        
        iid = tree.identify_row(event.y) # select row under mouse
        if iid: # mouse pointer over item
            tree.selection_set(iid)
            log.info(f'{event.x_root}, {event.y_root}') 
            tree.item(tree.get_children()[0], open=True)
        else: # mouse pointer not over item; no action required
            pass


    def on_select(self, event):
        tree = event.widget


    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first, last)





if __name__ == '__main__':
    master = tk.Tk()
    master.title = 'Treeview Manipulation'
    
    dir_browser = DirBrowser(master)
    dir_browser.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    

    master.mainloop()