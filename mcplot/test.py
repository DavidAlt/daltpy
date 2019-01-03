import tkinter as tk
from tkinter import ttk


class TreeFrame(tk.Frame):
    def __init__(self, parent):
        super(TreeFrame, self).__init__(parent, background='green')

        # setup the GUI components
        top = self._setup_top_panel(self)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        bottom = self._setup_bottom_panel(self)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
    
   
    def _setup_top_panel(self, parent_):
        f = tk.Frame(parent_)
        self.main_tree = ttk.Treeview(f, height=12)
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


    def _setup_bottom_panel(self, parent):
        btn_f = tk.Frame(parent, background='yellow')
        btn_f.pack(anchor=tk.S)

        btn_up = tk.Button(btn_f, text='Up')
        btn_up.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)
        
        btn_dn = tk.Button(btn_f, text='Down')
        btn_dn.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)
        
        btn_detach = tk.Button(btn_f, text='Detach')
        btn_detach.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)
        
        btn_reattach_sel = tk.Button(btn_f, text='Reattach sel')
        btn_reattach_sel.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)

        btn_reattach_all = tk.Button(btn_f, text='Reattach all')
        btn_reattach_all.pack(side=tk.LEFT, anchor=tk.S, padx=5, pady=5)
        
        return btn_f
     

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
    master.title = 'MCPlot'
    
    panes = tk.PanedWindow(master)
    panes.pack(fill=tk.BOTH, expand=True)


    left_panel = TreeFrame(panes)
    #left_panel.pack(fill=tk.BOTH, expand=True)
    
    right_panel = tk.Frame(panes, background='red', width=800)
    

    panes.add(left_panel)
    panes.add(right_panel)


    master.mainloop()