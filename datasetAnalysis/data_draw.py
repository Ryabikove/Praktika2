import os.path
import tkinter as tk
from datetime import datetime
from tkinter import filedialog

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import dataset

class DataDraw:
    root : tk.Tk
    data_set : pd.DataFrame
    last_mod_time : float
    graph : Figure
    axis : Axes
    canvas : FigureCanvasTkAgg
    x : int = 0
    y : int = 1

    def __init__(self, root : tk.Tk, data_set : pd.DataFrame) -> None:
        self.root = root
        self.data_set = data_set[dataset.numeric_cols]
        self.last_mod_time = os.path.getmtime(dataset.dataset_path)

        self.root.title("Data Draw")

        self.graph = Figure(dpi = 100)
        self.canvas = FigureCanvasTkAgg(self.graph, master = root)

        self.axis = self.graph.add_subplot(111)
        self.axis.grid(True)
        self.update_plot()

        self.canvas_widget = self.canvas.get_tk_widget()

        self.left_frame = tk.Frame(self.root)
        self.bottom_frame = tk.Frame(self.root)

        for i in range(self.data_set.shape[1]):
            button_l = tk.Button(self.left_frame, text = self.data_set.columns[i], command = lambda y = i: self.y_column_but(y))
            button_l.pack(padx = 5, pady = 5, fill = 'x')

            button_b = tk.Button(self.bottom_frame, text = self.data_set.columns[i], command = lambda x = i: self.x_column_but(x))
            button_b.pack(side = 'left', padx = 5, pady = 5)

        self.save_frame = tk.Frame(self.root)
        save_button = tk.Button(self.save_frame, text = 'Save graph', command = lambda : self.save_plot())
        save_button.pack(side = 'left', padx = 5, pady = 5)

        self.left_frame.grid(row = 0, column = 0, sticky = 'ns')
        self.canvas_widget.grid(row = 0, column = 1, sticky = 'nsew')
        self.bottom_frame.grid(row = 1, column = 1, sticky = 'ew')
        self.save_frame.grid(row = 1, column = 0, sticky = 'ew')

        self.root.grid_rowconfigure(0, weight = 1)
        self.root.grid_columnconfigure(1, weight = 1)

        self.root.update_idletasks()
        self.root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())

        self.autoupdate()

    def x_column_but(self, x : int) -> None:
        self.set_x(x)
        self.update_plot()

    def y_column_but(self, y : int) -> None:
        self.set_y(y)
        self.update_plot()

    def autoupdate(self) -> None:
        if os.path.exists(dataset.dataset_path):
            current = os.path.getmtime(dataset.dataset_path)

            if self.last_mod_time < current:
                self.data_set = pd.read_csv(dataset.dataset_path)[dataset.numeric_cols]
                self.last_mod_time = current
                self.update_plot()

        self.root.after(2000, self.autoupdate)

        return

    def save_plot(self) -> None:
        now = datetime.now()
        time_str=now.strftime("%H_%M_%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=f'graph{time_str}.png'
        )
        if path:
            self.graph.savefig(fname=path)

    def update_plot(self) -> None:
        self.axis.clear()
        self.axis.plot(self.data_set.iloc[:,self.x].tolist(), self.data_set.iloc[:,self.y].tolist(), marker = '*', linestyle = 'None',
                       color = 'red')
        self.axis.set_xlabel(self.data_set.columns[self.x])
        self.axis.set_ylabel(self.data_set.columns[self.y])
        self.canvas.draw()

    def set_x(self, x : int) -> None:
        self.x = x

    def set_y(self, y : int) -> None:
        self.y = y



if __name__ == "__main__":
    root = tk.Tk()
    app = DataDraw(root, dataset.df)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")