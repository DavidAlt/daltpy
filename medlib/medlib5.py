# For logging
import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('medlib3')
log.setLevel(logging.DEBUG)

# For user interface
import os, threading, queue
import tkinter as tk
from tkinter import ttk, filedialog

# For timing operations
from timeit import default_timer as timer
from functools import reduce

# For PDF operations and DOI extraction
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from io import StringIO
import re


# TODO: Threading / Queue
#   Not sure if the whole queue/listening bit is actually used
#   Implement multiple worker threads with queue to speed processing
# TODO: Report building
#   More robust logging (elapsed per file, per batch, total)
#   use hidden time column in trees 
# TODO: Right-click context menu to open file/folder at file location


###### HELPER FUNCTIONS ######
def convert_pdf_to_text(path):
    resource_manager = PDFResourceManager()
    return_string = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(resource_manager, return_string, codec=codec, laparams=laparams)
    file_path = open(path, 'rb')
    interpreter = PDFPageInterpreter(resource_manager, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(file_path, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    result = return_string.getvalue()

    file_path.close()
    device.close()
    return_string.close()

    return result

def extract_doi(path):
    pdf = convert_pdf_to_text(path)
    regx = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b'
    all_doi = re.findall(regx, pdf)
    unique = set(all_doi)
    if not unique:
        return False
    else:
        return unique

def format_elapsed_time(t):
        return "%d:%02d:%02d.%03d" % \
            reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
                [(t*1000,),1000,60,60])



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



class MedLib():

    def __init__(self):
        self.work_dir = os.getcwd()
        
        # setup the root window        
        self.master = tk.Tk()
        self.master.wm_title('MedLib')
        self.master.geometry('800x600')

        # setup the gui
        self.setup_toolbar(self.master)
        self.setup_workspace(self.master)
        self.setup_statusbar(self.master)

        # setup queue and start listening
        self.q = queue.Queue()
        self.master.after(100, self.listen_for_result)
        
        # start the UI loop
        self.master.mainloop()


    ###### GUI SETUP ######
    def setup_toolbar(self, master):
        toolbar = tk.Frame(master)
        toolbar.pack(fill=tk.X, expand=False, anchor=tk.N)
        tk.Button(toolbar, text='Load directory', command=self.on_load).pack(side=tk.LEFT, padx=3, pady=3)
        tk.Button(toolbar, text='Process selection', command=self.on_process).pack(side=tk.LEFT, padx=3, pady=3)
        tk.Button(toolbar, text='Reset', command=self.on_reset).pack(side=tk.LEFT, padx=3, pady=3)
        tk.Button(toolbar, text='Build report', command=self.on_build_report).pack(side=tk.RIGHT, padx=3, pady=3)
        tk.Button(toolbar, text='Export citations', command=self.on_export).pack(side=tk.RIGHT, padx=3, pady=3)

    def setup_workspace(self, master):
        workspace = ttk.Notebook(master)
        workspace.pack(fill=tk.BOTH, expand=True, padx=3, pady=1)

        self.dir_tree_frame = ScrollTree(workspace, 'Directory', 'Status')
        self.dir_tree_frame.pack(fill=tk.BOTH, expand=True)
        self.dir_tree = self.dir_tree_frame.tree
        self.dir_tree.column('info', minwidth=40, width=120, stretch=tk.NO)
        self.dir_tree.bind('<Double-Button-1>', self.on_dir_tree_dblclick)
        
        self.doi_tree_frame = ScrollTree(workspace, 'File', 'DOI')
        self.doi_tree_frame.pack(fill=tk.BOTH, expand=True)
        self.doi_tree = self.doi_tree_frame.tree
        self.doi_tree.column('info', minwidth=40, width=240, stretch=tk.NO)

        self.more_doi_tree_frame = ScrollTree(workspace, 'File', 'DOIs')
        self.more_doi_tree_frame.pack(fill=tk.BOTH, expand=True)
        self.more_doi_tree = self.more_doi_tree_frame.tree
        
        self.no_doi_tree_frame = ScrollTree(workspace, 'File', 'Path')
        self.no_doi_tree_frame.pack(fill=tk.BOTH, expand=True)
        self.no_doi_tree = self.no_doi_tree_frame.tree

        workspace.add(self.dir_tree_frame, text='  Unprocessed  ')
        workspace.add(self.doi_tree_frame, text='  Unique DOIs  ')
        workspace.add(self.more_doi_tree_frame, text='  Multiple DOIs  ')
        workspace.add(self.no_doi_tree_frame, text='  No DOIs  ')

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

        # populate tree with directories and PDF files
        for directory, subdir_list, file_list in os.walk(self.work_dir):
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
                self.dir_tree.detach(child)

        # update the info column with files remaining for each directory
        self.update_dir_tree_counts()

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
        
    def on_process(self):
        t = threading.Thread(target=self.process_selected)
        t.start()

    def on_reset(self):
        self.dir_tree.delete(*self.dir_tree.get_children())
        self.work_dir = os.getcwd()

    def on_export(self):
        f = tk.filedialog.asksaveasfile(mode='w', initialdir = os.getcwd(), 
            title = 'Export list of PDFs with a single DOI', 
            filetypes = (('Text files','*.txt'),('All files','*.*')),
            defaultextension='*.*')
        
        if f is None: # user cancels
            return
        
        for child in self.doi_tree.get_children():
            path = self.doi_tree.set(child, 'fullpath')
            name = self.doi_tree.item(child)['text']
            doi = self.doi_tree.set(child, 'info')
            f.write('TY  - JOUR\n')
            f.write(f'TI  - {name}\n')
            f.write(f'DO  - {doi}\n')
            f.write('ER  -\n')
            
        f.close()

    def on_build_report(self):
        # create a text file with the contents of each tree
        f = tk.filedialog.asksaveasfile(mode='w', initialdir = os.getcwd(),
            title = 'Build report',
            filetypes = (('Text files', '*.txt'), ('All files', '*.*')),
            defaultextension = '*.*')

        if f is None: 
            return

        # TODO: general statistics about the operation
        #   num files processed
        #   time to process
        #   num unique/more/no DOIs

        # loop through doi_tree
        f.write('# Files with a single unique DOI\n')
        for child in self.doi_tree.get_children():
            path = self.doi_tree.set(child, 'fullpath')
            name = self.doi_tree.item(child)['text']
            basedir = os.path.dirname(path)
            doi = self.doi_tree.set(child, 'info')
            f.write(f'  {name}\t{doi}\t{basedir}\n'.expandtabs(40))
        f.write('\n\n')        

        # loop through more_doi_tree and write file, path, DOIs
        f.write('# Files with multiple DOIs\n')
        for child in self.more_doi_tree.get_children():
            path = self.more_doi_tree.set(child, 'fullpath')
            name = self.more_doi_tree.item(child)['text']
            basedir = os.path.dirname(path)
            dois = self.more_doi_tree.set(child, 'info')
            f.write(f'  {name}\t{basedir}\t{dois}\n'.expandtabs(40))
        f.write('\n\n')

        # loop through no_doi_tree and write file, path
        f.write('# Files with no DOIs found\n')
        for child in self.no_doi_tree.get_children():
            path = self.no_doi_tree.set(child, 'fullpath')
            name = self.no_doi_tree.item(child)['text']
            basedir = os.path.dirname(path)
            f.write(f'  {name}\t{basedir}\n'.expandtabs(40))
        f.write('\n')


    ###### OTHER EVENTS ######
    def on_dir_tree_dblclick(self, event):
        selected = self.dir_tree.selection()[0]
        self.dir_tree.item(selected, open=True)

        if selected:
            t = threading.Thread(target=self.process_selected)
            t.start()


    ###### FUNCTIONS NEEDING THREADING ######
    def process_selected(self):
        if self.dir_tree.selection():
            start = timer()
            self.status.config(text='  Status:  WORKING ...')
            self.elapsed.config(text=f'Elapsed:  WORKING ...')
            self.master.update()

            for node in self.dir_tree.selection():
                if self.dir_tree.get_children(node):
                    for child in self.dir_tree.get_children(node):
                        self.process_node(child)
                else: 
                    self.process_node(node)
            
            self.status.config(text='  Status:  IDLE')
            self.master.update()
            end = timer()
            elapsed = format_elapsed_time(end-start)
            self.elapsed.config(text=f'Elapsed:  {elapsed}  ')
            
            # TODO: if nothing left to process, empty the tree

    def process_node(self, node):
        path = self.dir_tree.set(node, 'fullpath')
        filename = os.path.basename(path)
        dois = extract_doi(path)

        if dois: 
            if len(dois) == 1: # only 1 DOI
                self.dir_tree.set(node, 'info', 'processing ...')   
                self.master.update()

                doi = min(dois)
                self.doi_tree.insert(text=filename, parent='', index='end', values=(path, doi))
                
            else: # more than 1 DOI
                self.more_doi_tree.insert(text=filename, parent='', index='end', values=(path, dois))

            self.dir_tree.set(node, 'info', 'complete')

        else: # no DOIs
            self.no_doi_tree.insert(text=filename, parent='', index='end', values=(path, path))
        
        self.dir_tree.detach(node)
        self.update_dir_tree_counts()

    def listen_for_result(self):
        try: 
            # update UI based on results
            result = self.q.get(0)
            self.elapsed['text'] = f'Elapsed:  {result}'
            self.master.after(100, self.listen_for_result)
        except queue.Empty:
            self.master.after(100, self.listen_for_result)



if __name__ == '__main__':
    medlib = MedLib()