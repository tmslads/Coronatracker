from matplotlib import pyplot as plt, patheffects
import matplotlib
from matplotlib.font_manager import FontProperties


class BaseGraph:
    def __init__(self, **kwargs):
        matplotlib.use('agg')
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
        fp = FontProperties(family='Product Sans', variant='small-caps', stretch=420, weight='extra bold', size=20)

        self.canvas.suptitle(t=f"{_type}",
                             fontproperties=fp, color="#F9C027", ha='center', x=0.51,
                             path_effects=[patheffects.withSimplePatchShadow(shadow_rgbFace='#2C2C2C', alpha=0.7)],
                             clip_on=False, wrap=True)

        self.ax.set_title(label=f"{country}",
                          fontdict={'fontname': 'Product Sans', 'size': 21, 'weight': 'semibold', 'color': '#EEEEEE'},
                          loc='center', pad=6.0,
                          path_effects=[patheffects.withSimplePatchShadow(shadow_rgbFace='#2C2C2C', alpha=0.55),
                                        patheffects.Normal()], clip_on=False, wrap=True)

    def save_graph(self, path: str, color: str, **kwargs):
        self.canvas.savefig(fname=path, facecolor=color, **kwargs)
        plt.close(self.canvas)

    @staticmethod
    def show_graph():
        plt.show()  # Can't use figure instance here, cause we're using pure python shell & aren't managing event loop
