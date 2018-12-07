import logging
import tkinter as tk
from tkinter import ttk

logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('treeview')
log.setLevel(logging.DEBUG)

class TreeFrame(ttk.Frame):
    def __init__(self, parent):
        super(TreeFrame, self).__init__(parent)

        # declare the tree and any bindings
        self.tree = ttk.Treeview(self)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        # other virtual events include <<TreeviewOpen>> and <<TreeviewClose>>

        # style individual rows using tags
        self.tree.tag_configure('inner', foreground='cyan', background='black')

        # set up columns and headers
        self.tree.heading('#0', text='Item', anchor=tk.W)
        self.tree['columns'] = ('col1', 'col2', 'col3')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=10, width=50, stretch=tk.NO)
        
        # add content
        outer1 = self.tree.insert(parent='',index='end',text='First', values=('a', 'b', 'c'))
        inner1 = self.tree.insert(outer1, 'end', text='Inner1', values=('1','2','3'), tags='inner')
        
        outer2 = self.tree.insert(parent='',index='end',text='Second', values=('d', 'e', 'f'))
        outer3 = self.tree.insert(parent='',index='end',text='Third', values=('g', 'h', 'i'))
        
        # add to layout
        self.tree.pack(fill=tk.BOTH, expand=1) # fill the container


    def on_tree_select(self, event):
        # extract information from the event
        item_id = event.widget.focus() # equivalent to self.tree.selection()[0]; returns I004 (internally assigned number)
        item = event.widget.item(item_id) # returns {'text': 'Third', 'image': '', 'values': ['g', 'h', 'i'], 'open': 0, 'tags': ''}
        values = item['values'] # returns ['d', 'e', 'f']
        
        log.info(f'item:  {item}')
        log.info(f'item_id:  {item_id}')
        log.info(f'values:  {values}')
        #log.info(f'.selection():  {self.tree.selection()}') # returns ('I003',) on single selection
        #log.info(f'.selection()[0]:  {self.tree.selection()[0]}')

    def on_double_click(self, event):
        log.info(f'double click on {self.tree.selection()[0]}')

        


if __name__ == '__main__':
    log.info(f'tk version: {tk.TkVersion}')
    log.info(f'ttk version: {ttk.__version__}')
    root = tk.Tk()
    root.title = 'Treeview,  With Text'

    paned_w = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
    # first pane, which would get widgets gridded into it:
    L_pane = TreeFrame(paned_w)
    L_pane.pack(fill='both', expand=True)
    R_pane = ttk.Labelframe(paned_w, text='R_pane', width=100, height=100)   # second pane
    paned_w.add(L_pane)
    paned_w.add(R_pane)
    paned_w.pack(fill='both', expand=True)

    log.info(paned_w.pane(R_pane))
    #options = paned_w.paneconfigure(R_pane)
    #log.info(paned_w.panecget(paned_w.children[0],'minsize'))

    root.mainloop()