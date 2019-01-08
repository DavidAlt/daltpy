import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('medlib3')
log.setLevel(logging.DEBUG)

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import os
import threading
from pdf_get_doi import *

class DirBrowser(tk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.path = os.getcwd()

        self.setup_tree()


    def setup_tree(self):
        vsb = ttk.Scrollbar(self, orient="vertical")
        hsb = ttk.Scrollbar(self, orient="horizontal")

        self.tree = ttk.Treeview(self, columns=("fullpath", "type", "status"),
            displaycolumns="status", yscrollcommand=lambda f, l: self.autoscroll(vsb, f, l),
            xscrollcommand=lambda f, l: self.autoscroll(hsb, f, l))

        vsb['command'] = self.tree.yview
        hsb['command'] = self.tree.xview

        self.tree.heading("#0", text="Directory", anchor='w')
        self.tree.heading('status', text='Status', anchor='w')
        self.tree.column('status', stretch=0, width=100)

        self.populate()
        #self.populate_roots(self.tree)
        
        #self.tree.bind('<<TreeviewOpen>>', self.update_tree)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-Button-1>', self.on_dblclick)
        self.tree.bind('<Button-3>', self.on_rclick)

        # Arrange the tree and its scrollbars in the toplevel
        self.tree.grid(column=0, row=0, sticky='nswe')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def change_dir(self, new_path):
        self.path = new_path
        self.populate()
        #if os.path.isdir(new_path):
        #    os.chdir(new_path)
        #    self.tree.delete(*self.tree.get_children())
        #    self.populate_roots(self.tree)

    def populate(self):
        # clear the existing tree
        self.tree.delete(*self.tree.get_children())

        for directory, subdir_list, file_list in os.walk(self.path):
            # Do this when a (sub)directory is encountered
            node = self.tree.insert('', 'end', text=directory)
            self.tree.set(node, 'fullpath', directory)
            #print(self.tree.set(node, 'fullpath'))
            
            for file in file_list: # for the current directory
                #print(file)
                #filename = os.fsdecode(file)
                #file_path = os.path.join(subdir, filename)

                if file.endswith('.pdf'): 
                    pdf_path = os.path.join(directory, file)
                    pdf_node = self.tree.insert(node, 'end', text=file)
                    self.tree.set(pdf_node, 'fullpath', pdf_path)
                    #print(self.tree.set(pdf_node, 'fullpath'))


    def populate_tree(self, tree, node):
        log.info('')
        if tree.set(node, "type") != 'directory':
            return

        path = tree.set(node, "fullpath")
        tree.delete(*tree.get_children(node))

        parent = tree.parent(node)

        for p in os.listdir(path):
            ptype = None
            p = os.path.join(path, p).replace('\\', '/')
            
            if os.path.isdir(p): 
                ptype = "directory"
            elif os.path.isfile(p): 
                ptype = "file"

            fname = os.path.split(p)[1]
            #log.info(fname)
            
            if ptype == 'directory' or fname.endswith('.pdf'):
                id = tree.insert(node, "end", text=fname, values=[p, ptype], open=True)

                if ptype == 'directory':
                    tree.insert(id, 0, text="dummy")
                    tree.item(id, text=fname)
                elif ptype == 'file':
                    pass # set details for the file
                    tree.set(id, 'status', 'unprocessed')
        
        # Expand the root node
        tree.item(tree.get_children()[0], open=True)
        

    def populate_roots(self, tree):
        dir = os.path.abspath('.').replace('\\', '/')
        node = tree.insert('', 'end', text=dir, values=[dir, "directory"])
        self.populate_tree(tree, node)


    def update_tree(self, event):
        tree = event.widget
        self.populate_tree(tree, tree.focus())


    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first, last)


    def on_select(self, event):
        tree = event.widget


    def on_dblclick(self, event):
        # process the selected file or directory
        # pass the info to the main gui to process on a different thread?
        # basically it gets the DOI, then starts and stops the progressbar
        selected = self.tree.selection()[0]
        path = self.tree.set(selected, 'fullpath')
        #self.parent.start_progress()
        doi = get_doi(path)
        #self.parent.stop_progress()
        log.info(f'{path}:  {doi}')


    def on_rclick(self, event):
        tree = event.widget
        
        iid = tree.identify_row(event.y) # select row under mouse
        if iid: # mouse pointer over item
            tree.selection_set(iid)
            log.info(f'{event.x_root}, {event.y_root}') 
            tree.item(tree.get_children()[0], open=True)
        else: # mouse pointer not over item; no action required
            pass



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
        #f_dir = tk.Frame(self)
        self.dir_tree = DirBrowser(self)
        #self.dir_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        #vscroll1 = ttk.Scrollbar(f_dir, orient='vertical', command=self.dir_tree.yview)
        #vscroll1.pack(side=tk.RIGHT, fill='y')
        self.dir_tree.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

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

        # row 5 / status bar
        #self.statusbar = tk.Label(self, text='Status').grid(row=5, columnspan=4)
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="indeterminate")
        self.progress.grid(row=5, columnspan=4, sticky=tk.E)

    def start_progress(self):
        log.info('')
        self.progress.start()

    def stop_progress(self):
        log.info('')
        self.progress.stop()

    def on_btn_load(self):
        result = tk.filedialog.askdirectory(initialdir = "/",title = "Select directory")
        self.dir_tree.change_dir(result)

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
    
    
