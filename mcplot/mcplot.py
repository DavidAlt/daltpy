import tkinter as tk
from tkinter import ttk

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('MCPlot')
log.setLevel(logging.DEBUG)


class TreeFrame(tk.Frame):
    def __init__(self, parent):
        super(TreeFrame, self).__init__(parent, background='green')

        # setup the GUI components
        top = self._setup_top_panel(self)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        bottom = self._setup_bottom_panel(self)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

    
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


    def on_main_tree_select(self, event):
        pass


    def _setup_top_panel(self, parent):
        f = tk.Frame(parent)
        self.main_tree = ttk.Treeview(f, height=30)
        self.main_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, anchor=tk.CENTER, padx=5)
        vscroll = ttk.Scrollbar(f, orient='vertical', command=self.main_tree.yview)
        vscroll.pack(side=tk.RIGHT, fill='y')

        # set up columns and headers
        self.main_tree.heading('#0', text='Item', anchor=tk.W)
        self.main_tree['columns'] = ('X', 'Y', 'Z')
        for col in self.main_tree['columns']:
            self.main_tree.heading(col, text=col)
            self.main_tree.column(col, minwidth=40, width=40, stretch=tk.NO, anchor=tk.CENTER)
        self._populate_dummy_content(self.main_tree)

        return f

        # add bindings
        self.main_tree.bind('<<TreeviewSelect>>', self.on_main_tree_select)
        #self.main_tree.bind('<Double-Button-1>', self.on_main_tree_double_click)

        return f


    def _setup_bottom_panel(self, parent_):
        f = tk.Frame(parent_)
        
        btn_f = tk.Frame(f)
        btn_f.pack()

        btn_up = tk.Button(btn_f, text='Up', command=self.on_btn_up)
        btn_up.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)
        
        btn_dn = tk.Button(btn_f, text='Down', command=self.on_btn_down)
        btn_dn.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)
        
        btn_detach = tk.Button(btn_f, text='Detach', command=self.on_btn_detach)
        btn_detach.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)
        
        btn_reattach_sel = tk.Button(btn_f, text='Reattach sel', command=self.on_btn_reattach_sel)
        btn_reattach_sel.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)

        btn_reattach_all = tk.Button(btn_f, text='Reattach all', command=self.on_btn_reattach_all)
        btn_reattach_all.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)
        
        return f
     

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
    master.wm_title('MCPlot')
    master.state('zoomed')
    #master.iconbitmap("icon.ico")
    
    panes = tk.PanedWindow(master)
    panes.pack(fill=tk.BOTH, expand=True)

    left_panel = TreeFrame(panes)
    right_panel = tk.Frame(panes, background='red', width=800)

    panes.add(left_panel)
    panes.add(right_panel)


    master.mainloop()