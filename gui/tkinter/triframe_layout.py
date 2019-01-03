import tkinter as tk

if __name__ == '__main__':
    master = tk.Tk()
    master.title = 'Tri-Frame Layout'
    
    f_left = tk.Frame(master, background='yellow')
    f_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    f_up = tk.Frame(f_left, background='red', height=300, width=400)
    f_up.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    f_down = tk.Frame(f_left, background='blue', height=50, width=400)
    f_down.pack(side=tk.BOTTOM, fill=tk.X)

    f_right = tk.Frame(master, background='green', height=650, width=800)
    f_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    master.mainloop()