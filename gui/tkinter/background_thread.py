import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('bg threads')
log.setLevel(logging.DEBUG)

import tkinter as tk
from tkinter import ttk
import os, time, threading, queue


class ExampleApplication():
    
    def __init__(self):
        self.master = tk.Tk()
        self.master.wm_title('Background Threads')
        self.master.geometry('640x480')

        self.q = queue.Queue()

        # setup the gui
        gui = tk.Frame(self.master)
        gui.pack(expand=True, fill=tk.BOTH)
        self.msg = tk.Label(gui, text='No message')
        self.msg.pack() 
        tk.Button(gui, text='Update', command=self.on_btn_update).pack()
        tk.Button(gui, text='Reset', command=self.on_btn_reset).pack()

        self.master.after(100, self.listen_for_result)
        
        self.master.mainloop()


    def listen_for_result(self):
        #log.info('')
        try:
            self.result = self.q.get(0)
            self.msg['text'] = self.result
            self.master.after(100, self.listen_for_result)
            log.info(f'Result: {self.result}')
        except queue.Empty:
            self.master.after(100, self.listen_for_result)


    def start_work(self):
        t = threading.Thread(target=self.long_function)
        t.start()


    def long_function(self):
        time.sleep(2)
        self.q.put('Completed 2 second operation')

    def on_btn_update(self):
        log.info('')
        self.start_work()

    def on_btn_reset(self):
        self.msg['text'] = 'No message'


if __name__ == "__main__":
    the_app = ExampleApplication()