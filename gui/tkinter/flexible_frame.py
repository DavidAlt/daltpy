import tkinter as tk
from tkinter import ttk

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('flex_frame')
log.setLevel(logging.DEBUG)


class FlexFrame(tk.Frame):
    def __init__(self, parent, has_chkbox=True, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.label = tk.Label(self, text='Caption')
        self.label.pack(side=tk.LEFT)

        if has_chkbox:
            self.setup_chkbox()

        
    def setup_chkbox(self):
        self.chk = tk.Checkbutton(self)
        self.chk.pack(side=tk.RIGHT)

if __name__ == '__main__':
    
    master = tk.Tk()
    master.wm_title('FlexFrame')

    ff1 = FlexFrame(master, bg='red').pack()

    master.mainloop()        