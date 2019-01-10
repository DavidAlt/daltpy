import os, time
import tkinter as tk
from tkinter import ttk

class DirBrowser(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.path = os.getcwd()
        self.setup_tree()


    def setup_tree(self):
        self.tree = ttk.Treeview(self, columns=('status'))
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.tree.heading("#0", text="Directory", anchor='w')
        self.tree.heading('status', text='Status', anchor='w')

        self.tree.bind('<Double-Button-1>', self.on_dblclick)

        for directory, subdir_list, file_list in os.walk(self.path):
            node = self.tree.insert('', 'end', text=directory)

            for file in file_list: 
                self.tree.insert(node, 'end', text=file)


    def on_dblclick(self, event):
        selected = self.tree.selection()[0]

        # set status column to 'processing'
        self.tree.set(selected, 'status', 'processing ...')

        # simulate a time-consuming function
        # the real program extracts text from a PDF here
        time.sleep(4)

        # set status column to 'complete'
        self.tree.set(selected, 'status', 'complete')


if __name__ == '__main__':
    master = tk.Tk()
    tree = DirBrowser(master).pack(fill=tk.BOTH, expand=True)
    master.mainloop()