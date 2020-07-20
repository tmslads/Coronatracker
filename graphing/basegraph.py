from matplotlib import pyplot as plt, patheffects


class BaseGraph:
    def __init__(self, **kwargs):
        self.canvas, self.ax = plt.subplots(1, 1, figsize=(10, 8), **kwargs)  # Fig size is perfect for 1920x1080

        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

    def enable_grid(self, axis: str):
        self.ax.grid(b=True, axis=axis)  # Enable grid
        self.ax.set_axisbelow(True)  # Makes grid lines go behind line

    def spine_config(self, spine_color: str, visibility: float, line_width: float):
        self.ax.spines['bottom'].set_linewidth(line_width)
        self.ax.spines['left'].set_visible(visibility)

        self.ax.spines['left'].set_color(spine_color)
        self.ax.spines['bottom'].set_color(spine_color)

    def set_fig_color(self, color: str):
        self.canvas.patch.set_facecolor(color)
        self.ax.patch.set_facecolor(color)

    def set_locator_formatter(self, x_locator=None, x_formatter=None, y_locator=None, y_formatter=None):
        if x_locator is not None:
            self.ax.xaxis.set_major_locator(x_locator)
        if x_formatter is not None:
            self.ax.xaxis.set_major_formatter(x_formatter)

        if y_locator is not None:
            self.ax.yaxis.set_major_locator(y_locator)
        if y_formatter is not None:
            self.ax.yaxis.set_major_formatter(y_formatter)

    def set_title(self, _type: str, country: str):
        self.ax.set_title(label=f"{_type}\n{country}",
                          fontdict={'fontname': 'Product Sans', 'size': 21, 'weight': 'semibold', 'color': '#EEEEEE'},
                          loc='center', pad=6.0,
                          path_effects=[patheffects.SimpleLineShadow(shadow_color='#331C7C', alpha=0.8),
                                        patheffects.Normal()], clip_on=False, wrap=True)

    def save_graph(self, path: str, color: str, **kwargs):
        self.canvas.savefig(fname=path, facecolor=color, **kwargs)

    @staticmethod
    def show_graph():
        plt.show()  # Can't use figure instance here, cause we're using pure python shell & aren't managing event loop
