import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('dice_buttons')
log.setLevel(logging.DEBUG)

import random


class DiceButton(tk.Button):
    def __init__(self, parent, die='d6', sides=6, size='small', *args, **kwargs):
        tk.Button.__init__(self, parent, *args, **kwargs)

        self.name = die
        self.sides = sides
        self.num_dice = 1
        
        self.bind('<MouseWheel>', self.on_mouse_wheel)
        self.bind('<Button-1>', self.on_btn1)
        self.bind('<Button-2>', self.on_btn2)
        self.bind('<Button-3>', self.on_btn3)

        if die == 'd4':
            self.sides = 4
            if size == 'small': self.img = tk.PhotoImage(file='assets/d4-icon-32.gif')
            else: self.img = tk.PhotoImage(file='assets/d4-icon-64.gif')
        if die == 'd6': 
            self.sides = 6
            if size == 'small': self.img = tk.PhotoImage(file='assets/d6-icon-32.gif')
            else: self.img = tk.PhotoImage(file='assets/d6-icon-64.gif')
        if die == 'd8':
            self.sides = 8
            if size == 'small': self.img = tk.PhotoImage(file='assets/d8-icon-32.gif')
            else: self.img = tk.PhotoImage(file='assets/d8-icon-64.gif')
        if die == 'd10': 
            self.sides = 10
            if size == 'small': self.img = tk.PhotoImage(file='assets/d10-icon-32.gif')
            else: self.img = tk.PhotoImage(file='assets/d10-icon-64.gif')
        if die == 'd12':
            self.sides = 12
            if size == 'small': self.img = tk.PhotoImage(file='assets/d12-icon-32.gif')
            else: self.img = tk.PhotoImage(file='assets/d12-icon-64.gif')
        if die == 'd20': 
            self.sides = 20
            if size == 'small': self.img = tk.PhotoImage(file='assets/d20-icon-32.gif')
            else: self.img = tk.PhotoImage(file='assets/d20-icon-64.gif')
        self.config(image=self.img)


    def get_range(self):
        return self.num_dice * self.sides

    def on_mouse_wheel(self, event):
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            if self.num_dice > 1:
                self.num_dice -= 1
                self['text'] = self.name + ': ' + str(self.num_dice)
        if event.num == 4 or event.delta == 120:
            self.num_dice += 1
            self['text'] = self.name + ': ' + str(self.num_dice)
        log.info(f'{self.name}: {self.num_dice}')


    def on_btn1(self, event):
        log.info(self.roll())


    def on_btn2(self, event):
        if self.num_dice != 1:
            self.num_dice = 1


    def on_btn3(self, event):
        die_range = self.get_range()
        log.info(f'Current range: {self.num_dice} - {die_range}')


    def roll(self):
        result = 0
        for i in range(self.num_dice):
            result += random.randint(1, self.sides)
        return result



class DicePanel(tk.Frame):
    def __init__(self, parent, die='d6', sides=6, size='small', *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.die = DiceButton(self, die='d6', sides=6, size='small')
        self.die.pack(side=tk.LEFT)
        self.info = tk.Label(self, text=f'({self.die.num_dice} - {self.die.get_range()})')
        self.info.pack(side=tk.RIGHT)


if __name__ == '__main__':
    
    master = tk.Tk()
    master.wm_title('Buttons')

    d4 = DiceButton(master, die='d4').pack(pady=3)
    d6 = DiceButton(master, die='d6').pack(pady=3)
    d8 = DiceButton(master, die='d8').pack(pady=3)
    d10 = DiceButton(master, die='d10').pack(pady=3)
    d12 = DiceButton(master, die='d12').pack(pady=3)
    d20 = DiceButton(master, die='d20').pack(pady=3)

    dp = DicePanel(master, die=6).pack(pady=3)


    master.mainloop()        