import tkinter as tk

import pandas as pd
import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import dataset

class DataScatter:
    root : tk.Tk
    data_set : pd.DataFrame
    graph : Figure
    axis : Axes
    canvas : FigureCanvasTkAgg
    x : int = 0
    y : int = 1

    def __init__(self, root : tk.Tk, data_set : pd.DataFrame) -> None:
        self.root = root
        self.data_set = data_set

        self.root.title("Data Scatter")
        self.root.geometry("600x450")
        self.root.minsize(600, 400)

        self.graph = Figure(dpi=100)
        self.axis = self.graph.add_subplot(111)

        self.axis.plot(self.data_set.iloc[:,self.x].tolist(), self.data_set.iloc[:,self.y].tolist(), marker='*', linestyle='None',
                       color='red')
        self.axis.set_xlabel(self.data_set.columns[self.x])
        self.axis.set_ylabel(self.data_set.columns[self.y])
        self.axis.grid(True)

        self.canvas = FigureCanvasTkAgg(self.graph, self.root)
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_plot(self) -> None:
        self.axis.clear()
        self.axis.plot(self.x, self.y)
        self.canvas.draw()

    def set_x(self, x : int) -> None:
        self.x = x

    def set_y(self, y : int) -> None:
        self.y = y



if __name__ == "__main__":
    root = tk.Tk()
    app = DataScatter(root, dataset.df)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")