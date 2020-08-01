import matplotlib
from matplotlib import pyplot as plt, patheffects
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import Locator, Formatter


class BaseGraph:
    """Base class for handling and setting the desired design for the graphs. Is subclassed by `Plotter`.

    Attributes:
        canvas (Figure): Matplotlib's Figure object.
        ax (Axes): Matplotlib's Axis object.
    """

    def __init__(self, **kwargs) -> None:
        matplotlib.use('agg')
        self.canvas, self.ax = plt.subplots(figsize=(10, 8), **kwargs)  # Fig size is perfect for 1920x1080

        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

    def enable_grid(self, axis: str) -> None:
        """
        Enables grid on specified axis, and draws it behind the artists.

        Args:
            axis (str): The axis to enable grid on, either 'x' or 'y'.
        """
        self.ax.grid(b=True, axis=axis)  # Enable grid
        self.ax.set_axisbelow(True)  # Makes grid lines go behind line

    def spine_config(self, spine_color: str, visibility: float, line_width: float) -> None:
        """Set thickness and visibility of the spines.

        Args:
            spine_color (str): A hex color code, for the spine.
            visibility (float): Visibility of the spine, 1 for completely opaque, 0 for completely transparent.
            line_width (float): Thickness of the line, same values as above.
        """
        self.ax.spines['bottom'].set_linewidth(line_width)
        self.ax.spines['left'].set_visible(visibility)

        self.ax.spines['left'].set_color(spine_color)
        self.ax.spines['bottom'].set_color(spine_color)

    def set_fig_color(self, color: str) -> None:
        """Set the figure and axis color.
        Args:
            color (str): A hex color code.
        """
        self.canvas.patch.set_facecolor(color)
        self.ax.patch.set_facecolor(color)

    def set_locator_formatter(self, x_locator: Locator = None, x_formatter: Formatter = None, y_locator: Locator = None,
                              y_formatter: Formatter = None) -> None:
        """Set the locator(s) and/or formatter(s) for the axis/axes."""
        if x_locator is not None:
            self.ax.xaxis.set_major_locator(x_locator)
        if x_formatter is not None:
            self.ax.xaxis.set_major_formatter(x_formatter)

        if y_locator is not None:
            self.ax.yaxis.set_major_locator(y_locator)
        if y_formatter is not None:
            self.ax.yaxis.set_major_formatter(y_formatter)

    def set_title(self, _type: str, country: str) -> None:
        """
        Apply title for axis and for the figure, with appropriate font properties and styling.

        Args:
            _type (str): Title of the figure.
            country (str): Title of the axis.
        """
        fp = FontProperties(family='Product Sans', variant='small-caps', stretch=420, weight='extra bold', size=20)

        self.canvas.suptitle(t=f"{_type}", fontproperties=fp, color="#F9C027", ha='center', x=0.51,
                             path_effects=[patheffects.withSimplePatchShadow(shadow_rgbFace='#2C2C2C', alpha=0.7)],
                             clip_on=False, wrap=True)

        self.ax.set_title(label=f"{country}",
                          fontdict={'fontname': 'Product Sans', 'size': 21, 'weight': 'semibold', 'color': '#EEEEEE'},
                          loc='center', pad=6.0,
                          path_effects=[patheffects.withSimplePatchShadow(shadow_rgbFace='#2C2C2C', alpha=0.55)],
                          clip_on=False, wrap=True)

    def enable_legend(self) -> None:
        """Enable the legend for the graph, with appropriate font properties and styling."""
        legend = self.ax.legend(
            prop=FontProperties(family='Product Sans', variant='normal', stretch="semi-condensed", weight='book',
                                size=10), shadow=True, numpoints=2, markerscale=0.8, edgecolor='white')

        legend.set_title(title="LEGEND",
                         prop=FontProperties(family="Product Sans", weight="semibold", size=12, stretch="normal"))

    def save_graph(self, path: str, color: str, **kwargs) -> None:
        """
        Save the graph to the specified path, and color.

        Args:
            path (str): Path to store the image, will be stored as a .png
            color (str): A hex color code to save the image in.
        """
        self.canvas.savefig(fname=path, facecolor=color, **kwargs)
        plt.close(self.canvas)

    @staticmethod
    def show_graph() -> None:
        """Display the graph in interactive mode."""
        plt.show()  # Can't use figure instance here, cause we're using pure python shell & aren't managing event loop
