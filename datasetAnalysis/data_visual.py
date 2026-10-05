import os.path
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import filedialog

import pandas as pd

from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import colormaps
from matplotlib import colors

import numpy as np

import dataset

class DataVisual:
    root : tk.Tk
    data_set : pd.DataFrame
    last_mod_time : float
    graph : Figure
    axis : Axes
    canvas : FigureCanvasTkAgg
    x : int = 0
    y : int = 1
    style : str = 'GnBu'

    def __init__(self, root : tk.Tk, data_set : pd.DataFrame) -> None:
        self.root = root
        self.data_set = data_set
        self.last_mod_time = os.path.getmtime(dataset.dataset_path)

        self.root.title("Data Visual")

        # Create graph
        self.graph = Figure(dpi = 100)
        self.canvas = FigureCanvasTkAgg(self.graph, master = root)

        self.axis = self.graph.add_subplot(111)
        self.axis.grid(True)
        self.update_graph()

        self.canvas_widget_frame = self.canvas.get_tk_widget()

        # Create cmap menu
        self.cmap_frame = ttk.Frame(self.root)

        ttk.Label(self.cmap_frame, text="Color maps menu:").pack(side="left", padx=5, pady=5)
        self.combo = ttk.Combobox(self.cmap_frame, values = sorted(colormaps)[:29], state = 'readonly', width = 30)
        self.combo.set(self.style)
        self.combo.bind('<<ComboboxSelected>>', self.change_cmap)
        self.combo.pack(side="left", padx=5, pady=5)


        # Create column buttons
        self.left_frame = tk.Frame(self.root)
        self.bottom_frame = tk.Frame(self.root)

        for i in range(self.data_set.shape[1]):
            button_l = tk.Button(self.left_frame, text = self.data_set.columns[i], command = lambda y = i: self.y_column_but(y))
            button_l.pack(padx = 5, pady = 5, fill = 'x')

            button_b = tk.Button(self.bottom_frame, text = self.data_set.columns[i], command = lambda x = i: self.x_column_but(x))
            button_b.pack(side = 'left', padx = 5, pady = 5)

        # Create save button
        self.save_frame = tk.Frame(self.root)
        save_button = tk.Button(self.save_frame, text = 'Save graph', command = lambda : self.save_graph())
        save_button.pack(side = 'left', padx = 5, pady = 5)

        # Locate each frame
        self.cmap_frame.grid(row = 0, column = 1, sticky = 'nw')
        self.left_frame.grid(row = 1, column = 0, sticky = 'ns')
        self.canvas_widget_frame.grid(row = 1, column = 1, sticky ='nsew')
        self.bottom_frame.grid(row = 2, column = 1, sticky = 'ew')
        self.save_frame.grid(row = 2, column = 0, sticky = 'ew')

        self.root.grid_rowconfigure(0, weight = 1)
        self.root.grid_columnconfigure(1, weight = 1)

        self.root.update_idletasks()
        self.root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())

        self.autoupdate()

    def x_column_but(self, x : int) -> None:
        self.set_x(x)
        self.update_graph()

    def y_column_but(self, y : int) -> None:
        self.set_y(y)
        self.update_graph()

    def autoupdate(self) -> None:
        if os.path.exists(dataset.dataset_path):
            current = os.path.getmtime(dataset.dataset_path)

            if self.last_mod_time < current:
                self.data_set = pd.read_csv(dataset.dataset_path)[dataset.numeric_cols]
                self.last_mod_time = current
                self.update_graph()

        self.root.after(2000, self.autoupdate)

        return

    def save_graph(self) -> None:
        now = datetime.now()
        time_str=now.strftime("%H_%M_%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=f'graph{time_str}.png'
        )
        if path:
            self.graph.savefig(fname=path)

    def update_graph(self) -> None:
        self.axis.clear()
        self.axis.set_frame_on(True)
        self.axis.set_aspect('auto')

        x = self.data_set.iloc[:, self.x].tolist()
        y = self.data_set.iloc[:, self.y].tolist()

        cmap = colormaps[self.style]

        if self.x == self.y:
            if self.data_set.columns[self.x] in dataset.numeric_cols:
                counts, bins, patches = self.axis.hist(x, bins=10, edgecolor = 'black')
                norm = colors.Normalize(
                    vmin = float(counts.min()),
                    vmax = float(counts.max()),
                )

                self.axis.bar_label(patches, fmt = '%d', padding = 3)
                for i, patch in enumerate(patches):
                    patch.set_facecolor(cmap(norm(counts[i])))

            elif self.data_set.columns[self.x] in dataset.categorical_columns:
                values, counts = np.unique(x, return_counts=True)
                wedges, texts = self.axis.pie(counts, labels = values, startangle = 90)
                self.axis.axis("equal")

                norm = colors.Normalize(
                    vmin = float(counts.min()),
                    vmax = float(counts.max()),
                )

                for wedge, clr in zip(wedges, counts):
                    wedge.set_facecolor(cmap(norm(clr)))

            else:
                print(f"Error: Column {self.data_set.columns[self.x]} with index {self.x} not found in dataset.")
                exit(1)
        elif self.data_set.columns[self.x] in dataset.numeric_cols and self.data_set.columns[self.y] in dataset.categorical_columns:
            categories = np.unique(y)
            data = [self.data_set.loc[
                        y == c, self.data_set.columns[self.x]
                    ].to_numpy() for c in categories]

            bp = self.axis.boxplot(data, tick_labels = categories, orientation = "horizontal", patch_artist = True, widths = 0.6)

            boxes = bp['boxes']
            n = len(boxes)

            palette = cmap(np.linspace(0, 1, n))

            for box, color in zip(boxes, palette):
                box.set_facecolor(color)

            for median in bp['medians']:
                median.set_color('black')
                median.set_linewidth(1.5)

        elif self.data_set.columns[self.x] in dataset.categorical_columns and self.data_set.columns[self.y] in dataset.numeric_cols:
            values, counts = np.unique(x, return_counts=True)

            bars = self.axis.bar([str(v) for v in values], counts, edgecolor = 'black', linewidth = 1, )

            values = np.array(values)
            norm = colors.Normalize(
                vmin = float(values.min()),
                vmax = float(values.max()),
            )

            for bar, val in zip(bars, values):
                bar.set_facecolor(cmap(norm(val)))

        else:
            self.axis.scatter(x, y, marker = '*', cmap = self.style, c = np.hypot(x, y))

        self.axis.set_xlabel(self.data_set.columns[self.x])
        self.axis.set_ylabel(self.data_set.columns[self.y])
        self.canvas.draw()

    def change_cmap(self, event = None) -> None:
        new_style = self.combo.get()
        self.style = new_style

        self.update_graph()

    def set_x(self, x : int) -> None:
        self.x = x

    def set_y(self, y : int) -> None:
        self.y = y



if __name__ == "__main__":
    root = tk.Tk()
    app = DataVisual(root, dataset.df)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")