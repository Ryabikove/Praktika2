import os.path
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import filedialog

import pandas as pd

from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import colormaps
from matplotlib import colors

import numpy as np
from matplotlib.lines import Line2D

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
    style : str = 'GnBu'
    painting_mode : bool = False
    square_size : int = 7

    def __init__(self, root : tk.Tk, data_set : pd.DataFrame) -> None:
        self.root = root
        self.data_set = data_set
        self.last_mod_time = os.path.getmtime(dataset.dataset_path)
        self.paint_cids = []
        self.current_line = None
        self.current_xs = []
        self.current_ys = []

        self.root.title("Data Draw")

        # Create graph
        self.graph = Figure(dpi = 100)
        self.canvas = FigureCanvasTkAgg(self.graph, master = root)

        self.axis = self.graph.add_subplot(111)
        self.axis.grid(True)
        self.update_graph()

        self.canvas_widget_frame = self.canvas.get_tk_widget()

        # Create tool frame
        self.tool_frame = ttk.Frame(self.root)

        # Create cmap menu
        ttk.Label(self.tool_frame, text="Color maps menu:").pack(side = "left", padx = 5, pady = 5)
        self.combo = ttk.Combobox(self.tool_frame, values = sorted(colormaps)[:29], state = 'readonly', width = 30)
        self.combo.set(self.style)
        self.combo.bind('<<ComboboxSelected>>', self.change_cmap)
        self.combo.pack(side = "left", padx = 5, pady = 5)

        # Create draw menu
        self.draw_enable_b = ttk.Button(self.tool_frame, text = 'Painting mode: OFF', command = lambda: self.enable_painting_mode())
        self.draw_enable_b.pack(side = "left", padx = 5, pady = 5)


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
        self.tool_frame.grid(row = 0, column = 1, sticky ='nw')
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
        self.disable_painting_mode()
        self.set_x(x)
        self.update_graph()

    def y_column_but(self, y : int) -> None:
        self.disable_painting_mode()
        self.set_y(y)
        self.update_graph()

    def disable_painting_mode(self) -> None:
        if not self.painting_mode:
            return

        self.painting_mode = False
        for cid in self.paint_cids:
            self.canvas.mpl_disconnect(cid)

        self.current_line = None
        self.draw_enable_b.config(text = 'Painting mode: OFF')
        self.canvas_widget_frame.config(cursor = '')

    def enable_painting_mode(self) -> None:
        if self.painting_mode:
            self.disable_painting_mode()
            return

        self.painting_mode = True
        self.draw_enable_b.config(text = 'Painting mode: ON')
        self.canvas_widget_frame.config(cursor = 'pencil')

        self.paint_cids = [
            self.canvas.mpl_connect('button_press_event', self.on_paint_press),
            self.canvas.mpl_connect('button_release_event', self.on_paint_release),
            self.canvas.mpl_connect('motion_notify_event', self.on_paint_motion)

        ]

    def on_paint_press(self, event) -> None:
        if event.button == MouseButton.RIGHT:
            self.disable_painting_mode()
            return

        if event.button != MouseButton.LEFT:
            return

        self.current_xs, self.current_ys = [], []
        self._add_point(*self._event_to_px(event))

        self.current_line = Line2D(
            self.current_xs, self.current_ys,
            transform = self.graph.transFigure,
            linestyle = 'None',
            marker = 's',
            markersize = self.square_size,
            markeredgewidth = 0,
            color = 'red'
        )
        self.graph.add_artist(self.current_line)
        self.canvas.draw_idle()

    def on_paint_motion(self, event) -> None:
        if self.current_line is None:
            return

        px, py = self._event_to_px(event)
        lx, ly = self.last_px
        step = self._square_step_px()
        dist = np.hypot(px-lx, py-ly)

        if dist < step:
            return

        for i in range(1, int(dist // step) + 1):
            t = i * step / dist
            self._add_point(lx + (px - lx) * t, ly + (py - ly) * t)

        self.current_line.set_data(self.current_xs, self.current_ys)
        self.canvas.draw_idle()

    def on_paint_release(self, event) -> None:
        if event.button == MouseButton.LEFT:
            self.current_line = None


    def _event_to_px(self, event) -> tuple[float, float]:
        w, h = self.graph.bbox.width, self.graph.bbox.height
        return min(max(event.x, 0.0), w), min(max(event.y, 0.0), h)

    def _square_step_px(self) -> float:
        return self.square_size * self.graph.dpi / 72

    def _add_point(self, px: float, py: float) -> None:
        self.current_xs.append(px / self.graph.bbox.width)
        self.current_ys.append(py / self.graph.bbox.height)
        self.last_px = (px, py)

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
    app = DataDraw(root, dataset.df)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")