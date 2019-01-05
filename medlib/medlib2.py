import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('medlib_basic')
log.setLevel(logging.DEBUG)


class MedLibFrame(tk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent)

        #setup grid, 4 col x 5 row
        self.columnconfigure(0, pad=3, weight=1)
        self.columnconfigure(1, pad=3, weight=1)
        self.columnconfigure(2, pad=3, weight=1)
        self.columnconfigure(3, pad=3, weight=1)
        
        self.rowconfigure(0, pad=3)
        self.rowconfigure(1, pad=3, weight=2)
        self.rowconfigure(2, pad=3)
        self.rowconfigure(3, pad=3, weight=1)
        self.rowconfigure(4, pad=3)
        
        # row 0 = lbl | btn | lbl | none
        tk.Label(self, text='PDFs in selected directory').grid(row=0, column=0)
        tk.Button(self, text='Load ...', command=self.on_btn_load).grid(row=0, column=1)
        tk.Label(self, text='PDFs with DOIs').grid(row=0, column=2, sticky=tk.W)
        
        # row 1 = tr|ee | tr|ee
        f_dir = tk.Frame(self)
        self.dir_tree = ttk.Treeview(f_dir)
        self.dir_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        vscroll1 = ttk.Scrollbar(f_dir, orient='vertical', command=self.dir_tree.yview)
        vscroll1.pack(side=tk.RIGHT, fill='y')
        f_dir.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        f_doi = tk.Frame(self)
        self.doi_tree = ttk.Treeview(f_doi)
        self.doi_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=5)
        vscroll2 = ttk.Scrollbar(f_doi, orient='vertical', command=self.doi_tree.yview)
        vscroll2.pack(side=tk.RIGHT, fill='y')
        f_doi.grid(row=1, column=2, rowspan=3, columnspan=2, sticky=tk.NSEW)

        # set up columns and headers
        self.doi_tree.heading('#0', text='File', anchor=tk.W)
        self.doi_tree['columns'] = ('DOI')
        for col in self.doi_tree['columns']:
            self.doi_tree.heading(col, text=col)
            self.doi_tree.column(col, minwidth=40, width=240, stretch=tk.NO)

        # add bindings
        #self._tree.bind('<<TreeviewSelect>>', self.on_main_tree_select)
        #self._tree.bind('<Double-Button-1>', self.on_main_tree_double_click)


        # row 2 = lbl | lbl | tr|ee
        tk.Label(self, text='PDFs without DOIs').grid(row=2, column=0)
        tk.Label(self, text='PDFs with multiple DOIs').grid(row=2, column=1)

        # row 3 = lstbox | lstbox | tr|ee
        list_no_doi = tk.Listbox(self).grid(row=3, column=0, sticky=tk.NSEW)
        list_more_doi = tk.Listbox(self).grid(row=3, column=1, sticky=tk.NSEW)

        # row 4 = btn | btn | none | btn
        tk.Button(self, text='Export', command=self.on_btn_export_no_doi).grid(row=4, column=0)
        tk.Button(self, text='Export', command=self.on_btn_export_more_doi).grid(row=4, column=1)
        tk.Button(self, text='Export', command=self.on_btn_export_doi).grid(row=4, column=3)


    def on_btn_load(self):
        result = tk.filedialog.askdirectory(initialdir = "/",title = "Select directory")

    def on_btn_export_no_doi(self):
        log.info('')

    def on_btn_export_more_doi(self):
        log.info('')

    def on_btn_export_doi(self):
        log.info('')        

if __name__ == '__main__':
    
    master = tk.Tk()
    master.wm_title('medlib2')

    medlib = MedLibFrame(master)
    medlib.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    master.mainloop()