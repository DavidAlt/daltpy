import logging
import tkinter as tk
from tkinter import ttk

logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('treeview')
log.setLevel(logging.DEBUG)



class TreeFrame(tk.Frame):
    def __init__(self, parent):
        super(TreeFrame, self).__init__(parent)

        # setup the GUI components
        self.panes = tk.PanedWindow(self, orient=tk.VERTICAL)
        self.panes.pack(fill='both', expand=True)

        # setup the top panel (main tree)
        top = self._setup_top_panel(self.panes)
        self.panes.add(top)

        # setup the bottom panel (buttons, detached tree)
        bottom = self._setup_bottom_panel(self.panes)
        self.panes.add(bottom)

        #self._detached = []


    def _setup_top_panel(self, parent_):
        f = tk.Frame(parent_)
        self.main_tree = ttk.Treeview(f, height=12)
        self.main_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, anchor=tk.CENTER, padx=5)
        vscroll = ttk.Scrollbar(f, orient='vertical', command=self.main_tree.yview)
        vscroll.pack(side=tk.RIGHT, fill='y')

        # set up columns and headers
        self.main_tree.heading('#0', text='Item', anchor=tk.W)
        self.main_tree['columns'] = ('val[0]', 'val[1]', 'val[2]')
        for col in self.main_tree['columns']:
            self.main_tree.heading(col, text=col)
            self.main_tree.column(col, minwidth=40, width=40, stretch=tk.NO)
        self._populate_dummy_content(self.main_tree)

        # add bindings
        #self.main_tree.bind('<<TreeviewSelect>>', self.on_main_tree_select)
        #self.main_tree.bind('<Double-Button-1>', self.on_main_tree_double_click)

        return f

    def _setup_bottom_panel(self, parent_):
        f = tk.Frame(parent_)
        
        btn_f = tk.Frame(f)
        btn_f.pack()
        
        tree_f = tk.Frame(f)
        tree_f.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        btn_up = tk.Button(btn_f, text='Up')
        btn_up.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        
        btn_dn = tk.Button(btn_f, text='Down')
        btn_dn.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        
        btn_detach = tk.Button(btn_f, text='Detach')
        btn_detach.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        
        btn_reattach_all = tk.Button(btn_f, text='Reattach all')
        btn_reattach_all.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        
        btn_reattach_sel = tk.Button(btn_f, text='Reattach sel')
        btn_reattach_sel.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        
        self.detached_tree = ttk.Treeview(tree_f)
        self.detached_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, pady=5, padx=5)

        vscroll = ttk.Scrollbar(tree_f, orient='vertical', command=self.detached_tree.yview)
        vscroll.pack(side=tk.RIGHT, fill='y')

        # setup the Treeview
        self.detached_tree.heading('#0', text='id', anchor=tk.W)
        self.detached_tree['columns'] = ('parent', 'relative index')
        for col in self.detached_tree['columns']:
            self.detached_tree.heading(col, text=col)
            self.detached_tree.column(col, minwidth=10, width=30, stretch=tk.NO)
        
        return f
     

    def _populate_dummy_content(self, tree):
                # populate with dummy content
        
        # style individual rows using tags
        tree.tag_configure('inner', foreground='grey')

        outer1 = tree.insert(parent='',index='end',text='First', 
            values=('A', 'B', 'C'), open=True)
        tree.insert(outer1, 'end', text='Inner1_1', values=('1','2','3'), tags='inner')
        tree.insert(outer1, 'end', text='Inner1_2', values=('4','5','6'), tags='inner')
        
        outer2 = tree.insert(parent='',index='end',text='Second', 
            values=('D', 'E', 'F'), open=True)
        tree.insert(outer2, 'end', text='Inner2_1', values=('7','8','9'), tags='inner')
        tree.insert(outer2, 'end', text='Inner2_2', values=('10','11','12'), tags='inner')
        
        outer3 = tree.insert(parent='',index='end',text='Third', 
            values=('G', 'H', 'I'), open=True)
        tree.insert(outer3, 'end', text='Inner3_1', values=('13','14','15'), tags='inner')
        tree.insert(outer3, 'end', text='Inner3_2', values=('16','17','18'), tags='inner')
        
        outer4 = tree.insert(parent='',index='end',text='Fourth', 
            values=('J', 'K', 'L'), open=True)
        tree.insert(outer4, 'end', text='Inner4_1', values=('19','20','21'), tags='inner')
        tree.insert(outer4, 'end', text='Inner4_2', values=('22','23','24'), tags='inner')

        outer5 = tree.insert(parent='',index='end',text='Fifth', 
            values=('M', 'N', 'O'), open=True)
        tree.insert(outer5, 'end', text='Inner5_1', values=('25','26','27'), tags='inner')
        tree.insert(outer5, 'end', text='Inner5_2', values=('28','29','30'), tags='inner')    


if __name__ == '__main__':
    master = tk.Tk()
    master.title = 'Treeview Manipulation'
    
    tree_frame = TreeFrame(master)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    master.mainloop()