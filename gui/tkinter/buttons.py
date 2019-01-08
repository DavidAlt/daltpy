import tkinter as tk
from tkinter import ttk

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('buttons')
log.setLevel(logging.DEBUG)



class ScrollButton(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        tk.Button.__init__(self, parent, *args, **kwargs)
        self.bind("<MouseWheel>", self.mouse_wheel)

    def mouse_wheel(self, event):
        count = 0
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            count -= 1
        if event.num == 4 or event.delta == 120:
            count += 1
        log.info(count)




if __name__ == '__main__':
    
    master = tk.Tk()
    master.wm_title('Buttons')

    btn = tk.Button(master, text='Normal').pack()
    img_btn = tk.Button(master, text='Image').pack()
    scl_btn = ScrollButton(master, text='Scroll').pack()

    master.mainloop()        