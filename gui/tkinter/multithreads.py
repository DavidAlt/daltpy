# For logging
import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('medlib3')
log.setLevel(logging.DEBUG)

# For user interface
import os, threading, queue, time
import tkinter as tk
from tkinter import ttk, filedialog

# For timing operations
from timeit import default_timer as timer
from functools import reduce


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


###### HELPER FUNCTIONS ######
def lengthy_task(node):
    log.info('')
    time.sleep(3)


def format_elapsed_time(t):
        return "%d:%02d:%02d.%03d" % \
            reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
                [(t*1000,),1000,60,60])


class NodeWorker(threading.Thread):
    def __init__(self, q, *args, **kwargs):
        self.q = q
        #self.node = node
        super().__init__(*args, **kwargs)
    
    def run(self):
        while True:
            try:
                node = self.q.get(timeout=3)  # 3s timeout
            except queue.Empty:
                return
            # do whatever work you have to do on work
            node_id = node[0]
            node_name = node[1]
            node_path = node[2]
            
            time.sleep(4)
            log.info(f'{node_id}:  {node_name},  {node_path}')

            self.q.task_done()


class MedLib():

    def __init__(self):
        self.work_dir = os.getcwd()
        
        # setup the root window        
        self.master = tk.Tk()
        self.master.wm_title('Multi-threading')
        self.master.geometry('800x600')

        # setup the gui
        self.setup_toolbar(self.master)
        self.setup_workspace(self.master)
        self.setup_statusbar(self.master)

        # populate with working directory
        self.populate_dir_tree()

        # setup queue and start listening
        self.q = queue.Queue()
        #self.threads = []
        #self.master.after(100, self.listen_for_result)
        
        # start the UI loop
        self.master.mainloop()


    def do_work(self):
        while True:
            try:
                node = self.q.get(timeout=3)
            except queue.Empty:
                return
            
            # Do work here
            node_id = node[0]
            node_name = node[1]
            node_path = node[2]
            
            time.sleep(4)
            log.info(f'{node_id}:  {node_name},  {node_path}')

            self.q.task_done()
            


    ###### GUI SETUP ######
    def setup_toolbar(self, master):
        toolbar = tk.Frame(master)
        toolbar.pack(fill=tk.X, expand=False, anchor=tk.N)
        self.btn_load = tk.Button(toolbar, text='Load queue', command=self.on_load).pack(side=tk.LEFT, padx=3, pady=3)
        tk.Button(toolbar, text='Process queue', command=self.on_process).pack(side=tk.LEFT, padx=3, pady=3)
        tk.Button(toolbar, text='Clear queue', command=self.on_reset).pack(side=tk.LEFT, padx=3, pady=3)
        tk.Button(toolbar, text='Queue info', command=self.on_build_report).pack(side=tk.RIGHT, padx=3, pady=3)
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
        # Populate the queue from the selected items. 
        # You have to send the actual data, since tkinter will hang
        # if anything other than the main thread touches gui objects
        if self.dir_tree.selection():
            for node in self.dir_tree.selection():
                if self.dir_tree.get_children(node):
                    for child in self.dir_tree.get_children(node):
                        node_id = child
                        node_name = self.dir_tree.item(child)['text']
                        node_path = self.dir_tree.set(child, 'fullpath')
                        self.q.put((node_id, node_name, node_path))
                else: 
                    node_id = node
                    node_name = self.dir_tree.item(node)['text']
                    node_path = self.dir_tree.set(node, 'fullpath')
                    self.q.put((node_id, node_name, node_path))

        
    def on_process(self):
        # Process the queue
        # Start the worker threads
        
        start = timer()
        self.status.config(text='  Status:  WORKING ...')
        self.elapsed.config(text=f'Elapsed:  WORKING ...')
        self.master.update()

        items_in_queue = len(list(self.q.queue))
        if items_in_queue <= 100:
            num_workers = items_in_queue
        else:
            num_workers = 100 # hard cap of 100
        
        # start the workers
        log.info(f'Number of threads for this run: {num_workers}')
        for i in range(num_workers):
            #Worker(self.q).start()
            #threading.Thread(target=self.do_work).start()
            NodeWorker(self.q).start()

        
        
        # block until the queue is empty/work done
        # this has the effect of blocking the app
        # by NOT using q.join(), you can continue to interact
        self.q.join() 


        self.status.config(text='  Status:  IDLE')
        self.master.update()
        end = timer()
        elapsed = format_elapsed_time(end-start)
        self.elapsed.config(text=f'Elapsed:  {elapsed}  ')



    def on_reset(self):
        # Clear the queue
        with self.q.mutex:
            self.q.queue.clear()
        


    def on_export(self):
        # print contents of the queue
        pass


    def on_build_report(self):
        qsize = len(list(self.q.queue))
        log.info(f'Queue size: {qsize}')
        #for elem in list(self.q.queue):
        #    log.info(f'Queue contents: {elem}')


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