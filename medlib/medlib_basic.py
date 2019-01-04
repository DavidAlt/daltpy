import tkinter as tk
from tkinter import ttk

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('medlib_basic')
log.setLevel(logging.DEBUG)

from pdf_get_doi import *



class MedLibFrame1(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text='Path: ').pack()
        
        self.e = tk.Entry(self)
        self.e.pack(fill=tk.X, padx=5, pady=5)
        
        btn_file = tk.Button(self, text='File', command=self.on_btn_file)
        btn_file.pack(pady=5)
        btn_dir = tk.Button(self, text='Dir', command=self.on_btn_dir)
        btn_dir.pack(pady=5)
        btn_recursive = tk.Button(self, text='Dir (recursive)', command=self.on_btn_recursive)
        btn_recursive.pack(pady=5)

        self.tree = ttk.Treeview(self, height=10)
        self.tree.pack(expand=True, fill=tk.BOTH, padx=5)

        # set up columns and headers
        self.tree.heading('#0', text='File', anchor=tk.W)
        self.tree['columns'] = ('DOI')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=40, width=240, stretch=tk.NO)


    def on_btn_file(self):
        #doi = get_doi(self.e.get()) # get a single file
        dois = get_doi_from_dir(self.e.get())

        for k, v in dois.items():
            self.tree.insert('', 'end', text=k, values=(v))
    

    def on_btn_dir(self):
        dois = get_doi_from_dir(self.e.get())

        for k, v in dois.items():
            self.tree.insert('', 'end', text=k, values=(v))


    def on_btn_recursive(self):
        dois = get_doi_from_dir(self.e.get(), recursive=True)

        for k, v in dois.items():
            self.tree.insert('', 'end', text=k, values=(v))            


if __name__ == '__main__':
    
    master = tk.Tk()
    master.wm_title('medlib_basic')
    master.geometry('800x600')

    medlib1 = MedLibFrame1(master)
    medlib1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    

    master.mainloop()