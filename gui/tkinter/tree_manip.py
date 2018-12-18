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
        inner2 = self.tree.insert(outer1, 'end', text='Inner2', values=('4','5','6'), tags='inner')
        
        outer2 = self.tree.insert(parent='',index='end',text='Second', values=('d', 'e', 'f'))
        inner3 = self.tree.insert(outer2, 'end', text='Inner3', values=('7','8','9'), tags='inner')
        outer3 = self.tree.insert(parent='',index='end',text='Third', values=('g', 'h', 'i'))
        
        # add to layout
        self.tree.pack(fill=tk.BOTH, expand=1) # fill the container


    def on_tree_select(self, event):
        # extract information from the event
        item_id = event.widget.focus() # equivalent to self.tree.selection()[0]; returns I004 (internally assigned number)
        item = event.widget.item(item_id) # returns {'text': 'Third', 'image': '', 'values': ['g', 'h', 'i'], 'open': 0, 'tags': ''}
        values = item['values'] # returns ['d', 'e', 'f']


    def on_double_click(self, event):
        pass

    def move_selection_up(self):
        try:
            self.tree.selection()[0]
        except IndexError:
            log.error('IndexError: nothing selected')
        else:
            items = self.tree.selection()
            for item in items:
                tree_frame.tree.move(item, self.tree.parent(item), self.tree.index(item)-1)
    

    def move_selection_down(self):
        try:
            self.tree.selection()[0]
        except IndexError:
            log.error('IndexError: nothing selected')
        else:
            items = self.tree.selection()
            for item in items:
                self.tree.move(item, self.tree.parent(item), self.tree.index(item)+1)


if __name__ == '__main__':
    master = tk.Tk()
    master.title = 'Treeview Manipulation'

    def on_btn_up():
        tree_frame.move_selection_up()
            

    def on_btn_dn():
        tree_frame.move_selection_down()


    btn_frame = tk.Frame(master)
    btn_up = tk.Button(btn_frame, text='Up', command=on_btn_up)
    btn_dn = tk.Button(btn_frame, text='Down', command=on_btn_dn)
    btn_up.pack()
    btn_dn.pack()

    tree_frame = TreeFrame(master)
    tree_frame.pack(side=tk.LEFT)
    btn_frame.pack(side=tk.RIGHT)

    master.mainloop()