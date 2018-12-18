import logging
import tkinter as tk
from tkinter import ttk

logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('treeview')
log.setLevel(logging.DEBUG)



class TreePropertyFrame(tk.Frame):
    def __init__(self, parent):
        super(TreePropertyFrame, self).__init__(parent)

        self._detached = [] # stores data of detached items
        self.e_text = tk.StringVar()
        self.e_val0 = tk.StringVar()
        self.e_val1 = tk.StringVar()
        self.e_val2 = tk.StringVar()
        self._item_backup = ['','','','']

        # setup the GUI components
        outer_panes = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        outer_panes.pack(fill=tk.BOTH, expand=True)
        
        # setup the left side of outer panes (Treeview panel)
        inner_panes = tk.PanedWindow(outer_panes, orient=tk.VERTICAL)
        top = self._setup_top_panel(inner_panes)
        inner_panes.add(top)
        bottom = self._setup_bottom_panel(inner_panes)
        inner_panes.add(bottom)
        outer_panes.add(inner_panes)

        # setup the right side of outer panes (property editor)
        prop_editor = self._setup_right_panel(outer_panes)
        outer_panes.add(prop_editor, padx=10, pady=5)

    
    # Helper Functions
    def get_item_depth(self, tree, item_id):
        last_id = item_id
        depth = 0
        
        while tree.parent(last_id):
            depth += 1
            last_id = tree.parent(last_id)
        
        #log.info(f'{item_id} has a depth of {depth}')
        return depth

    def _update_detached_tree(self):
        # reset detached_tree
        for i in self.detached_tree.get_children():
            self.detached_tree.delete(i)
                
        # repopulate from the _detached list
        for item_id, parent_, index_, depth_ in self._detached:
            self.detached_tree.insert(text=item_id, parent='', index='end', values=(parent_, index_, depth_))

    # Events
    def on_btn_up(self):
        try:
            self.main_tree.selection()[0]
        except IndexError:
            log.error('IndexError: nothing selected')
        else:
            items = self.main_tree.selection()
            for item in items:
                self.main_tree.move(item, self.main_tree.parent(item), self.main_tree.index(item)-1)


    def on_btn_down(self):
        try:
            self.main_tree.selection()[0]
        except IndexError:
            log.error('IndexError: nothing selected')
        else:
            items = self.main_tree.selection()
            for item in items:
                self.main_tree.move(item, self.main_tree.parent(item), self.main_tree.index(item)+1)


    def on_btn_detach(self):
        try:
            self.main_tree.selection()[0]
        except IndexError:
            log.error('IndexError: nothing selected')
        else:
            for id in self.main_tree.selection(): # store info about current selection
                item = (id, self.main_tree.parent(id), self.main_tree.index(id), self.get_item_depth(self.main_tree, id))
                self._detached.append(item)
            for id in self.main_tree.selection(): # remove items in selection
                self.main_tree.detach(id)
        self._update_detached_tree()


    def on_btn_reattach_sel(self):
        log.warning('Does not handle case of child reattachment when parent is detached.')
        try:
            self.detached_tree.selection()[0]
        except IndexError:
            log.error('IndexError: nothing selected')
        else:
            for i in self.detached_tree.selection():
                item_id = self.detached_tree.item(i, option='text')
                values = self.detached_tree.item(i, option='values')
                parent = values[0]
                index = values[1]

                #if parent is in detached_tree: 
                    #log.warning('Cannot re-attach child while parent is detached.')
                    #continue
                #else:

                self.main_tree.move(item_id, parent, index)
                self.detached_tree.delete(i)

                # match the detached_tree item to the _detached list and remove it
                match = [item for item in self._detached if item[0] == item_id]
                self._detached.remove(match[0])

            self._update_detached_tree()


    def on_btn_reattach_all(self):
        for item_id, parent, index, depth in self._detached:
            #log.info(f'id: {item_id}    parent: {parent}    relative index: {index}     depth: {depth}')
            self.main_tree.move(item_id, parent, index)

        self._detached.clear()
        self._update_detached_tree()

    def on_btn_reset(self):
        self.e_text.set(self._item_backup[0])
        self.e_val0.set(self._item_backup[1])
        self.e_val1.set(self._item_backup[2])
        self.e_val2.set(self._item_backup[3])
        self.on_btn_apply()

    def on_btn_apply(self):
        try:
            self.main_tree.selection()[0]
        except IndexError:
            pass
        else:
            item = self.main_tree.selection()[0]
            new_values = []
            new_values.append(self.e_val0.get())
            new_values.append(self.e_val1.get())
            new_values.append(self.e_val2.get())

            self.main_tree.item(item, text=self.e_text.get())
            self.main_tree.item(item, values=new_values)
        

    def on_main_tree_select(self, event):
        try:
            self.main_tree.selection()[0]
        except IndexError: # nothing selected
            # clear the backup values
            self._item_backup[0] = ''
            self._item_backup[1] = ''
            self._item_backup[2] = ''
            self._item_backup[3] = ''
            # clear the Entry boxes
            self.e_text.set('')
            self.e_val0.set('')
            self.e_val1.set('')
            self.e_val2.set('')
        else:
            item_id = self.main_tree.selection()[0]
            text = self.main_tree.item(item_id, option='text')
            values = self.main_tree.item(item_id, option='values')
            # Backup the original values
            self._item_backup[0] = text
            self._item_backup[1] = values[0]
            self._item_backup[2] = values[1]
            self._item_backup[3] = values[2]
            # Fill the Entry boxes
            self.e_text.set(text)
            self.e_val0.set(values[0])
            self.e_val1.set(values[1])
            self.e_val2.set(values[2])


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
            self.main_tree.column(col, minwidth=40, width=40, stretch=tk.NO, anchor=tk.CENTER)
        self._populate_dummy_content(self.main_tree)

        # add bindings
        self.main_tree.bind('<<TreeviewSelect>>', self.on_main_tree_select)
        #self.main_tree.bind('<Double-Button-1>', self.on_main_tree_double_click)

        return f


    def _setup_bottom_panel(self, parent_):
        f = tk.Frame(parent_)
        
        btn_f = tk.Frame(f)
        btn_f.pack()
        
        tree_f = tk.Frame(f)
        tree_f.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        btn_up = tk.Button(btn_f, text='Up', command=self.on_btn_up)
        btn_up.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        
        btn_dn = tk.Button(btn_f, text='Down', command=self.on_btn_down)
        btn_dn.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        
        btn_detach = tk.Button(btn_f, text='Detach', command=self.on_btn_detach)
        btn_detach.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        
        btn_reattach_sel = tk.Button(btn_f, text='Reattach sel', command=self.on_btn_reattach_sel)
        btn_reattach_sel.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)

        btn_reattach_all = tk.Button(btn_f, text='Reattach all', command=self.on_btn_reattach_all)
        btn_reattach_all.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        
        self.detached_tree = ttk.Treeview(tree_f)
        self.detached_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, pady=5, padx=5)

        vscroll = ttk.Scrollbar(tree_f, orient='vertical', command=self.detached_tree.yview)
        vscroll.pack(side=tk.RIGHT, fill='y')

        # setup the Treeview
        self.detached_tree.heading('#0', text='Original id', anchor=tk.W)
        self.detached_tree['columns'] = ('Parent', 'Relative index', 'Depth')
        for col in self.detached_tree['columns']:
            self.detached_tree.heading(col, text=col)
            self.detached_tree.column(col, minwidth=10, width=100, stretch=tk.NO, anchor=tk.CENTER)
        
        return f
     

    def _setup_right_panel(self, parent):
        prop_frame = tk.Frame(parent, width=300)
        prop_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(prop_frame, text='Text').grid(row=0, column=0, sticky=tk.EW, pady=1)
        tk.Label(prop_frame, text='val[0]').grid(row=1, column=0, sticky=tk.EW, pady=1)
        tk.Label(prop_frame, text='val[1]').grid(row=2, column=0, sticky=tk.EW, pady=1)
        tk.Label(prop_frame, text='val[2]').grid(row=3, column=0, sticky=tk.EW, pady=1)

        self.e1 = tk.Entry(prop_frame, textvariable=self.e_text).grid(row=0, column=1, columnspan=2, sticky=tk.EW)
        self.e2 = tk.Entry(prop_frame, textvariable=self.e_val0).grid(row=1, column=1, columnspan=2, sticky=tk.EW)
        self.e3 = tk.Entry(prop_frame, textvariable=self.e_val1).grid(row=2, column=1, columnspan=2, sticky=tk.EW)
        self.e4 = tk.Entry(prop_frame, textvariable=self.e_val2).grid(row=3, column=1, columnspan=2, sticky=tk.EW)

        tk.Button(prop_frame, text='Reset', command=self.on_btn_reset).grid(row=4, column=1, pady=5)
        tk.Button(prop_frame, text='Apply', command=self.on_btn_apply).grid(row=4, column=2)

        return prop_frame


    def _populate_dummy_content(self, tree):
                # populate with dummy content
        
        # style individual rows using tags
        tree.tag_configure('inner', foreground='grey')

        outer1 = tree.insert(parent='',index='end',text='First', 
            values=('A', 'B', 'C'), open=True)
        tree.insert(outer1, 'end', text='Inner1_1', values=('1','2','3'), tags='inner')
        inner1 = tree.insert(outer1, 'end', text='Inner1_2', values=('4','5','6'), tags='inner')
        tree.insert(inner1, 'end', text='Deeper', values=(25,50,75))
        
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
    
    tree_frame = TreePropertyFrame(master)
    tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    

    master.mainloop()