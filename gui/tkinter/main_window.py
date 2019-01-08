import tkinter as tk
from tkinter import ttk

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('main_win')
log.setLevel(logging.DEBUG)



class MainWindow(tk.Frame, menu=True, toolbar=True, statusbar=True):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        if menu: self.setup_menu()
        if toolbar: self.setup_toolbar()
        if statusbar: self.setup_statusbar()





if __name__ == '__main__':
    
    master = tk.Tk()
    master.wm_title('Main Window')

    mw = MainWindow(master)
    mw.pack()

    master.mainloop()                