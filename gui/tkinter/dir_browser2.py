# For logging
import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('dir_browser')
log.setLevel(logging.DEBUG)

# For user interface
import tkinter as tk
from tkinter import ttk, filedialog
import os


class ScrollTree(tk.Frame):
    def __init__(self, parent, item_label, info_label):
        super().__init__(parent)
        self.parent = parent

        vsb = ttk.Scrollbar(self, orient='vertical')
        hsb = ttk.Scrollbar(self, orient='horizontal')

        self.tree = ttk.Treeview(self, 
            columns=('fullpath', 'info', 'time'),  displaycolumns='info', 
            yscrollcommand=lambda f, l: self.autoscroll(vsb, f, l),
            xscrollcommand=lambda f, l: self.autoscroll(hsb, f, l))

        vsb['command'] = self.tree.yview
        hsb['command'] = self.tree.xview

        self.tree.heading("#0", text=item_label, anchor='w')
        self.tree.heading('info', text=info_label, anchor='w')

        # Arrange the tree and its scrollbars in the toplevel
        self.tree.grid(column=0, row=0, sticky='nswe')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first, last)



class DirBrowser():

    def __init__(self):
        self.work_dir = os.getcwd()
        
        # setup the root window        
        self.master = tk.Tk()
        self.master.wm_title('Directory Browser')
        self.master.geometry('800x600')

        # setup the gui
        self.setup_toolbar(self.master)
        self.setup_workspace(self.master)
        self.setup_statusbar(self.master)

        # start the UI loop
        self.master.mainloop()


    ###### GUI SETUP ######
    def setup_toolbar(self, master):
        toolbar = tk.Frame(master)
        toolbar.pack(fill=tk.X, expand=False, anchor=tk.N)
        tk.Button(toolbar, text='Load directory', command=self.on_load).pack(side=tk.LEFT, padx=3, pady=3)
        #tk.Button(toolbar, text='Process selection', command=self.on_process).pack(side=tk.LEFT, padx=3, pady=3)
        tk.Button(toolbar, text='Reset', command=self.on_reset).pack(side=tk.LEFT, padx=3, pady=3)
        tk.Button(toolbar, text='Build report', command=self.on_build_report).pack(side=tk.RIGHT, padx=3, pady=3)
        #tk.Button(toolbar, text='Export citations', command=self.on_export).pack(side=tk.RIGHT, padx=3, pady=3)

    def setup_workspace(self, master):
        self.dir_tree_frame = ScrollTree(master, 'Directory', 'Status')
        self.dir_tree_frame.pack(fill=tk.BOTH, expand=True)
        self.dir_tree = self.dir_tree_frame.tree
        self.dir_tree.column('info', minwidth=40, width=120, stretch=tk.NO)
        #self.dir_tree.bind('<Double-Button-1>', self.on_dir_tree_dblclick)


    def setup_statusbar(self, master):
        status_bar = ttk.Frame(master, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, expand=False, anchor=tk.S)

        self.status = tk.Label(status_bar, text='Status:  IDLE')
        self.status.pack(side=tk.LEFT, padx=3, pady=2)

        handle = ttk.Sizegrip(status_bar)
        handle.pack(side=tk.RIGHT, anchor=tk.SE)

        self.elapsed = tk.Label(status_bar, text='')
        self.elapsed.pack(side=tk.RIGHT, padx=3)
        
    def populate_dir_tree(self):
        # clear the existing tree
        self.dir_tree.delete(*self.dir_tree.get_children())

        abspath = os.path.abspath(self.work_dir)
        root_node = self.dir_tree.insert('', 'end', text=abspath, open=True)
        self.process_directory(root_node, abspath)

        # populate tree with directories and PDF files
        '''for directory, subdir_list, file_list in os.walk(self.work_dir):
            node = self.dir_tree.insert('', 'end', text=directory)
            self.dir_tree.set(node, 'fullpath', directory)

            for file in file_list:
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(directory, file)
                    pdf_node = self.dir_tree.insert(node, 'end', text=file)
                    self.dir_tree.set(pdf_node, 'fullpath', pdf_path)

        # remove directories without PDFs (i.e., those without children)
        for child in self.dir_tree.get_children():
            if not self.dir_tree.get_children(child):
                self.dir_tree.detach(child)'''

        # update the info column with files remaining for each directory
        #self.update_dir_tree_counts()

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)

            if abspath.endswith('.pdf'):
                node = self.dir_tree.insert(parent, 'end', text=p, open=False)
                #print(f'{abspath}')

            # it's a file; insert it
            #node = self.dir_tree.insert(parent, 'end', text=p, open=False)
            
            # if not a PDF, remove it
            #if not abspath.endswith('.pdf'):
            #    print(f'{p} is not a pdf')
            #    self.dir_tree.detach(node)
            
            # it's a directory; call recursively
            if isdir:
                self.process_directory(node, abspath)


    def update_dir_tree_counts(self):
        for child in self.dir_tree.get_children():
            path = self.dir_tree.set(child, 'fullpath')
            if os.path.isdir(path):
                num_children = len(self.dir_tree.get_children(child))
                msg = f'{num_children} remaining'
                self.dir_tree.set(child, 'info', msg)


    ###### BUTTON FUNCTIONS ######
    def on_load(self):
        result = tk.filedialog.askdirectory(initialdir = os.getcwd(), 
            title = 'Select directory')
        
        if result is None: 
            return
        else:
            self.work_dir = result  # update the working directory
            self.populate_dir_tree()
        
    

    def on_reset(self):
        self.dir_tree.delete(*self.dir_tree.get_children())
        self.work_dir = os.getcwd()

    
    def on_build_report(self):
        # create a text file with the contents of each tree
        f = tk.filedialog.asksaveasfile(mode='w', initialdir = os.getcwd(),
            title = 'Build report',
            filetypes = (('Text files', '*.txt'), ('All files', '*.*')),
            defaultextension = '*.*')

        if f is None: 
            return

        pass




if __name__ == '__main__':
    dir_browser = DirBrowser()