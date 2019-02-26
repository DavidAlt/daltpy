# This version uses map and pool for multithreading
from multiprocessing.dummy import Pool as ThreadPool

# For logging
import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('medlib')
log.setLevel(logging.DEBUG)

# For user interface
import os, threading, queue, time
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

    filename = os.path.basename(path)

    #for page in PDFPage.get_pages(file_path, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
    try:
        log.info(f'Converting {filename}')
        for page in PDFPage.get_pages(file_path, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=False):
            interpreter.process_page(page)

        result = return_string.getvalue()

        file_path.close()
        device.close()
        return_string.close()

        return result
    except Exception as ex:
        log.error(f'Exception of type {type(ex).__name__} thrown on: {path}')
        pass
        # PDFPasswordIncorrect

def extract_doi(path):
    # Look into limiting what goes in the try block
    pdf = convert_pdf_to_text(path)
    regx = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b'
    try:
        all_doi = re.findall(regx, pdf)
        unique = set(all_doi)
        if not unique:
            return False
        else:
            return unique
    except Exception as ex:
        log.error(f'Exception of type {type(ex).__name__} thrown on: {path}')
        pass



def format_elapsed_time(t):
        return "%d:%02d:%02d.%03d" % \
            reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
                [(t*1000,),1000,60,60])

def process_node(node):
    node_id = node[0]
    node_name = node[1]
    path = node[2]
    filename = os.path.basename(path)
    
    dois = extract_doi(path)

    if dois: 
        if len(dois) == 1: # only 1 DOI
            doi = min(dois)
            result = {'origin_id': node_id, 'target': 'doi_tree', 'text': filename, 'path': path, 'info': doi}
        else: # more than 1 DOI
            result = {'origin_id': node_id, 'target': 'more_doi_tree', 'text': filename, 'path': path, 'info': dois}
    else: # no DOIs
        result = {'origin_id': node_id, 'target': 'no_doi_tree', 'text': filename, 'path': path, 'info': ''}

    return result


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



class NodeWorker(threading.Thread):
    def __init__(self, q, tree_q, *args, **kwargs):
        self.q = q
        self.tree_q = tree_q
        super().__init__(*args, **kwargs)
    
    def run(self):
        while True:
            try:
                node = self.q.get(timeout=3)  # 3s timeout
            except queue.Empty:
                return
            
            # Do the work
            node_id = node[0]
            node_name = node[1]
            path = node[2]
            filename = os.path.basename(path)
            
            dois = extract_doi(path)

            if dois: 
                if len(dois) == 1: # only 1 DOI
                    doi = min(dois)
                    result = {'origin_id': node_id, 'target': 'doi_tree', 'text': filename, 'path': path, 'info': doi}
                    self.tree_q.put(result)
                    
                else: # more than 1 DOI
                    result = {'origin_id': node_id, 'target': 'more_doi_tree', 'text': filename, 'path': path, 'info': dois}
                    self.tree_q.put(result)

            else: # no DOIs
                result = {'origin_id': node_id, 'target': 'no_doi_tree', 'text': filename, 'path': path, 'info': ''}
                self.tree_q.put(result)

            self.q.task_done()



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

        # setup queues and start listening
        self.q = queue.Queue()
        self.tree_update_queue = queue.Queue()
        self.master.after(100, self.update_trees)
        
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
        #self.dir_tree.bind('<Double-Button-1>', self.on_dir_tree_dblclick)
        
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
        # setup the data
        node_queue = []

        # Start the timer
        t1 = timer()
        self.status.config(text='  Status:  WORKING ...')
        self.elapsed.config(text=f'Elapsed:  WORKING ...')
        self.master.update()

        # Populate the queue from the selected items
        if self.dir_tree.selection():
            for node in self.dir_tree.selection():
                if self.dir_tree.get_children(node):
                    for child in self.dir_tree.get_children(node):
                        node_id = child
                        node_name = self.dir_tree.item(child)['text']
                        node_path = self.dir_tree.set(child, 'fullpath')
                        #self.q.put((node_id, node_name, node_path))
                        node_queue.append((node_id, node_name, node_path))
                else: 
                    node_id = node
                    node_name = self.dir_tree.item(node)['text']
                    node_path = self.dir_tree.set(node, 'fullpath')
                    #self.q.put((node_id, node_name, node_path))
                    node_queue.append((node_id, node_name, node_path))

        num_workers = 100
        pool = ThreadPool(num_workers)

        results = pool.map(process_node, node_queue)
        pool.close()
        pool.join() # waits until ALL tasks are completed
        # omitting .join() lets each process/thread run independently, 
        # but will mess up the total time elapsed since it's no longer considering it as one process
        
        t2 = timer()
        log.info(f'Total elapsed: {format_elapsed_time(t2-t1)}')
        
        # Do something with the results
        
        for result in results:
            print(result)
        
        
        # Start the worker threads
        '''items_in_queue = len(list(self.q.queue))
        if items_in_queue <= 200:
            num_workers = items_in_queue
        else:
            num_workers = 200 # hard cap
        log.info(f'Number of threads for current batch: {num_workers}')

        # start the workers
        for i in range(num_workers):
            NodeWorker(self.q, self.tree_update_queue).start()'''

        # Block until the queue is empty/work done; this freezes the GUI
        # Omitting it lets you interact with the GUI, but messes up timer
        #self.q.join() 

        # Finish the timer
        self.status.config(text='  Status:  IDLE')
        self.master.update()
        #end = timer()
        elapsed = format_elapsed_time(t2-t1)
        self.elapsed.config(text=f'Elapsed:  {elapsed}  ')

    def on_reset(self):
        self.dir_tree.delete(*self.dir_tree.get_children())
        self.doi_tree.delete(*self.doi_tree.get_children())
        self.more_doi_tree.delete(*self.more_doi_tree.get_children())
        self.no_doi_tree.delete(*self.no_doi_tree.get_children())
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

    def update_trees(self):
        # This loop checks the queue for messages every 100 milliseconds
        try: 
            # update UI based on results
            result = self.tree_update_queue.get(0)
            origin_id = result['origin_id']
            target_tree = result['target']
            target_text = result['text']
            target_path = result['path']
            target_info = result['info']
            #log.info(f'updating tree: {origin_id}, {target_tree}, {target_text}, {target_path}, {target_info}')

            if target_tree == 'doi_tree':
                self.doi_tree.insert(text=target_text, parent='', index='end', values=(target_path, target_info))
            elif target_tree == 'more_doi_tree':
                self.more_doi_tree.insert(text=target_text, parent='', index='end', values=(target_path, target_info))
            elif target_tree == 'no_doi_tree':
                self.no_doi_tree.insert(text=target_text, parent='', index='end', values=(target_path, target_path))

            self.dir_tree.detach(origin_id)
            self.update_dir_tree_counts()

            self.master.after(100, self.update_trees)

        except queue.Empty:
            self.master.after(100, self.update_trees)



if __name__ == '__main__':
    medlib = MedLib()