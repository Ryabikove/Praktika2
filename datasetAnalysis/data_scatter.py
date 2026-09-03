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
    x : list
    y : list

    def __init__(self, root : tk.Tk, data_set : pd.DataFrame) -> None:
        self.root = root
        self.data_set = data_set

        self.root.title("Data Scatter")
        self.root.geometry("600x450")
        self.root.minsize(600, 400)

        self.graph = Figure(dpi=100)
        self.axis = self.graph.add_subplot(111)
        self.x = self.data_set.iloc[:,0].tolist()
        self.y = self.data_set.iloc[:,1].tolist()

        self.axis.plot(self.x, self.y, marker='o', linestyle='None', color='red', label='Data')
        self.axis.set_title("Data Scatter")
        self.axis.set_xlabel("x")
        self.axis.set_ylabel("y")
        self.axis.legend()
        self.axis.grid(True)

        self.canvas = FigureCanvasTkAgg(self.graph, self.root)
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_plot(self) -> None:
        self.axis.clear()
        self.axis.plot(self.x, self.y)
        self.canvas.draw()

    def set_x(self, x : list) -> None:
        self.x = x

    def set_y(self, y : list) -> None:
        self.y = y



if __name__ == "__main__":
    root = tk.Tk()
    app = DataScatter(root, dataset.df)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")