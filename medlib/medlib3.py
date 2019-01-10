import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('medlib3')
log.setLevel(logging.DEBUG)

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import os
from timeit import default_timer as timer
from functools import reduce

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

        self.tree = ttk.Treeview(self, columns=('fullpath', 'status'),
            displaycolumns='status', yscrollcommand=lambda f, l: self.autoscroll(vsb, f, l),
            xscrollcommand=lambda f, l: self.autoscroll(hsb, f, l))

        vsb['command'] = self.tree.yview
        hsb['command'] = self.tree.xview

        self.tree.heading("#0", text="Directory", anchor='w')
        self.tree.heading('status', text='Status', anchor='w')
        #self.tree.column('status', stretch=0, width=100)

        self.populate()
        
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


    def populate(self):
        # clear the existing tree
        self.tree.delete(*self.tree.get_children())

        for directory, subdir_list, file_list in os.walk(self.path):
            # Do this when a (sub)directory is encountered
            node = self.tree.insert('', 'end', text=directory)
            self.tree.set(node, 'fullpath', directory)
            
            for file in file_list: # for the current directory

                if file.endswith('.pdf'): 
                    pdf_path = os.path.join(directory, file)
                    pdf_node = self.tree.insert(node, 'end', text=file)
                    self.tree.set(pdf_node, 'fullpath', pdf_path)

        # remove directories without PDFs (i.e., those without children)
        for child in self.tree.get_children():
            if not self.tree.get_children(child):
                self.tree.detach(child)

        self.update_parent_count()


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


    def secondsToStr(self, t):
        return "%d:%02d:%02d.%03d" % \
            reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
                [(t*1000,),1000,60,60])


    def process_selected(self):
        if self.tree.selection():
            
            start = timer()
            self.parent.status_left.config(text='  Status:  WORKING ...')
            self.parent.parent.update()

            for node in self.tree.selection():
                if self.tree.get_children(node):
                    for child in self.tree.get_children(node):
                        self.process_node(child)
                else: 
                    self.process_node(node)
            
            self.parent.status_left.config(text='  Status:  IDLE')
            self.parent.parent.update()
            end = timer()
            elapsed = self.secondsToStr(end-start)
            self.parent.status_right.config(text=f'Elapsed:  {elapsed}  ')
        else: # nothing selected, do nothing 
            pass


    def process_node(self, node):
        path = self.tree.set(node, 'fullpath')
        dois = get_doi(path)

        if dois: 
            filename = os.path.basename(path)

            if len(dois) == 1: # only 1 DOI
                self.tree.set(node, 'status', 'processing ...')   
                self.parent.update()
                
                doi = get_doi(path)
                pretty_doi = min(doi)
                self.parent.doi_tree.insert(text=filename, parent='', index='end', values=(path, pretty_doi))
                
            else: # more than 1 DOI
                log.info('multiple')
                self.parent.more_doi_tree.insert(text=filename, parent='', index='end', values=(path, dois))

            self.tree.set(node, 'status', 'complete')

        else: # no DOIs
            self.parent.list_no_doi.insert(tk.END, path)
        
        self.tree.detach(node)

        self.update_parent_count()


    def update_parent_count(self):
        for child in self.tree.get_children():
            path = self.tree.set(child, 'fullpath')
            if os.path.isdir(path):
                num_children = len(self.tree.get_children(child))
                msg = f'{num_children} remaining'
                self.tree.set(child, 'status', msg)


    def on_dblclick(self, event):
        selected = self.tree.selection()[0]
        self.tree.item(selected, open=True)
        self.process_selected()


    def on_rclick(self, event):
        pass


class MedLibFrame(tk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

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
        tk.Button(self, text='Load ...', command=self.on_btn_load).grid(row=0, column=0, sticky=tk.W)
        tk.Button(self, text='Process Selected', command=self.on_btn_process).grid(row=0, column=1)
        tk.Label(self, text='PDFs with DOIs').grid(row=0, column=2, sticky=tk.W)
        
        # row 1 = tr|ee | tr|ee
        self.dir_tree = DirBrowser(self)
        self.dir_tree.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        f_doi = tk.Frame(self)
        self.doi_tree = ttk.Treeview(f_doi, columns=('fullpath', 'doi'), displaycolumns='doi')
        self.doi_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=5)
        vscroll2 = ttk.Scrollbar(f_doi, orient='vertical', command=self.doi_tree.yview)
        vscroll2.pack(side=tk.RIGHT, fill='y')
        f_doi.grid(row=1, column=2, rowspan=3, columnspan=2, sticky=tk.NSEW)

        # set up columns and headers
        self.doi_tree.heading('#0', text='File', anchor=tk.W)
        self.doi_tree.heading('doi', text='DOI', anchor='w')

        # row 2 = lbl | lbl | tr|ee
        tk.Label(self, text='PDFs without DOIs').grid(row=2, column=0)
        tk.Label(self, text='PDFs with multiple DOIs').grid(row=2, column=1)

        # row 3 = lstbox | lstbox | tr|ee
        self.list_no_doi = tk.Listbox(self)
        self.list_no_doi.grid(row=3, column=0, sticky=tk.NSEW)

        f_more_doi = tk.Frame(self)
        self.more_doi_tree = ttk.Treeview(f_more_doi, columns=('fullpath', 'doi'), displaycolumns='doi')
        self.more_doi_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=5)
        vscroll2 = ttk.Scrollbar(f_more_doi, orient='vertical', command=self.more_doi_tree.yview)
        vscroll2.pack(side=tk.RIGHT, fill='y')
        f_more_doi.grid(row=3, column=1, sticky=tk.NSEW)

        # set up columns and headers
        self.more_doi_tree.heading('#0', text='File', anchor=tk.W)
        self.more_doi_tree.heading('doi', text='DOI', anchor='w')

        # row 4 = btn | btn | none | btn
        tk.Button(self, text='Export', command=self.on_btn_export_no_doi).grid(row=4, column=0)
        tk.Button(self, text='Export', command=self.on_btn_export_more_doi).grid(row=4, column=1)
        tk.Button(self, text='Export', command=self.on_btn_export_doi).grid(row=4, column=3)

        # row 5
        self.status_left = tk.Label(self, text='  Status:  IDLE')
        self.status_left.grid(row=5, column=0, columnspan=2, sticky=tk.W)
        self.status_right = tk.Label(self, text='')
        self.status_right.grid(row=5, column=2, columnspan=2, sticky=tk.E)


    def on_btn_load(self):
        result = tk.filedialog.askdirectory(initialdir = os.getcwd(), 
            title = 'Select directory')
        self.dir_tree.change_dir(result)


    def on_btn_process(self):
        self.dir_tree.process_selected()


    def on_btn_export_no_doi(self):
        f = tk.filedialog.asksaveasfile(mode='w', initialdir = os.getcwd(), 
            title = 'Export list of PDFs without DOIs', 
            filetypes = (('Text files','*.txt'),('All files','*.*')),
            defaultextension='*.*')
        if f is None: # user cancels
            return
        for i, item in enumerate(self.list_no_doi.get(0, tk.END)):
            f.write(item)
        f.close()


    def on_btn_export_more_doi(self):
        f = tk.filedialog.asksaveasfile(mode='w', initialdir = os.getcwd(), 
            title = 'Export list of PDFs with multiple DOIs', 
            filetypes = (('Text files','*.txt'),('All files','*.*')),
            defaultextension='*.*')
        
        if f is None: # user cancels
            return
        
        for child in self.more_doi_tree.get_children():
            path = self.more_doi_tree.set(child, 'fullpath')
            name = self.more_doi_tree.item(child)['text']
            doi = self.more_doi_tree.set(child, 'doi')
            f.write(f'{path}\t{name}\t{doi}\n')
        
        f.close()


    def on_btn_export_doi(self):
        f = tk.filedialog.asksaveasfile(mode='w', initialdir = os.getcwd(), 
            title = 'Export list of PDFs with a single DOI', 
            filetypes = (('Text files','*.txt'),('All files','*.*')),
            defaultextension='*.*')
        
        if f is None: # user cancels
            return
        
        for child in self.doi_tree.get_children():
            path = self.doi_tree.set(child, 'fullpath')
            name = self.doi_tree.item(child)['text']
            doi = self.doi_tree.set(child, 'doi')
            f.write(f'{path}\t{name}\t{doi}\n')
            
        f.close()
        


if __name__ == '__main__':
    
    master = tk.Tk()
    master.wm_title('MedLib - DOI Extraction')

    medlib = MedLibFrame(master)
    medlib.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    master.mainloop()
    
    
