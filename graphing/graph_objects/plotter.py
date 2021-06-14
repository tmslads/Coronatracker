from matplotlib import patheffects
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter, date2num
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import EngFormatter, PercentFormatter

from ..graph_objects.basegraph import BaseGraph


class Plotter(BaseGraph):
    """
    Class to fine-tune the graph requested by the user. Subclasses BaseGraph.

    Attributes:
        x (list): The list of values to use for the x-axis in the graph.
        y (list): The list of values to use for the y-axis in the graph.
        logscale (bool): Pass True, if the y-axis should be in log scale.
    """
    fp = FontProperties(fname='graphing/mpl_fonts/Product_Sans_Regular.ttf', variant='small-caps', stretch=460,
                        weight='demibold', size=11)

    def __init__(self, x: list, y: list, logscale: bool = False):
        super().__init__()
        self.x = x
        self.y = y
        self.logscale = logscale

    def line_plot(self, line_color: str, line_width: int or float, moving_avg: list = False, **kwargs):
        """
        Generates the line plot from the given data with suitable font and style properties.

        Args:
            line_color (str): A hex color code, for the line.
            line_width (int|float): The width of the line to be drawn.
            moving_avg (list): Pass a list, this will be used instead of the `y` attribute.
        """
        if moving_avg:
            self.ax.plot(self.x, moving_avg, color=line_color, linewidth=line_width, **kwargs)
        else:
            self.ax.plot(self.x, self.y, color=line_color, linewidth=line_width, **kwargs)

        if self.logscale:
            self.ax.set_yscale(value='log')
            # Set the y axis label as 'LOG' for beauty-
            self.ax.set_ylabel(ylabel="LOG", y=0.9, ha='right', rotation='horizontal', labelpad=6,
                               bbox={'boxstyle': 'round', 'facecolor': '#FFDD47'}, fontproperties=self.fp)

    def bar_plot(self, bar_color: str, line_width: int, **kwargs):
        """
        Generates the bar plot from the given data with suitable font and style properties.

        Args:
            bar_color (str): A hex color code, for the bars.
            line_width (int|float): The width of the bar to be drawn.
        """
        self.ax.bar(x=self.x, height=self.y, color=bar_color, linewidth=line_width, **kwargs)

    def axis_locator_formatter(self, unit: str = ""):
        """
        Sets the locator and formatter of the x-axis and formatter for the y-axis. Extends `set_locator_formatter` from
        BaseGraph.

        Args:
            unit (str): Optional, pass '%' to set the y-axis formatter as PercentFormatter. Default: ''. When default
                value is used, the y-axis formatter will use Engineering format.
        """
        # Set date and a clever formatter-
        locator = AutoDateLocator()
        formatter = ConciseDateFormatter(locator)

        # Convert cases numbers to human readable form- Eg: 7000 -> 7k, 1.356 -> 1.5%
        if unit == "%":
            human_format = PercentFormatter(decimals=1)
        else:
            human_format = EngFormatter(unit=unit, sep="")

        super().set_locator_formatter(x_locator=locator, x_formatter=formatter, y_formatter=human_format)

    def add_annotation(self, is_pct: bool = False):
        """
        Draws a arrow head and the last y data value onto the graph at the appropriate position with the appropriate
        font properties.

        Args:
            is_pct (bool): Pass True, if y values represent percentages. Default: False.
        """
        # Put arrow head on last case
        annotation = self.ax.annotate("", xy=(date2num(self.x[-1]) + 3, self.y[-1]), xytext=(1, 0),
                                      textcoords='offset points', ha='center',
                                      arrowprops={'facecolor': '#02D4F5', 'headwidth': 12, 'edgecolor': '#13292B'},
                                      annotation_clip=False)

        case_no = format(int(self.y[-1]), ',d').__len__()

        if case_no >= 7:
            offset = 50
        elif 5 <= case_no:
            offset = 42
        elif case_no == 4:
            offset = 35
        else:
            offset = 30

        self.ax.annotate(text=f"{round(self.y[-1], 1)}%" if is_pct else format(int(self.y[-1]), ',d'), ha='center',
                         va='center', fontweight='bold', xy=(annotation.xy[0], annotation.xy[-1]),
                         xytext=((35 if is_pct else offset), 0), textcoords="offset points", annotation_clip=False,
                         path_effects=[patheffects.withSimplePatchShadow(shadow_rgbFace='#2C2C2C', alpha=0.2)],
                         clip_on=False, wrap=True, font='graphing/mpl_fonts/Product_Sans_Bold.ttf', color='#FFFFFF',
                         fontsize=14)

    def tick_config(self):
        """Configures the tick properties such as labels by applying the appropriate font and styles."""
        # Change tick properties such as tick markers, color, transparency, etc-
        self.ax.tick_params(axis='x', grid_alpha=0.4, color='#FFFFFF', direction='inout', grid_color='#FFFFFF',
                            grid_linewidth=0.0, labelcolor="#EBF7F7")
        self.ax.tick_params(axis='y', colors='#FFFFFF', grid_alpha=0.5, grid_color='#F65BF1', left=False,
                            direction='inout', grid_linewidth=0.3, labelcolor="#EBF7F7", which='both')

        for xtick in self.ax.xaxis.get_major_ticks():
            xtick.label.set_fontproperties(self.fp)
            xtick.label.set_path_effects([patheffects.withSimplePatchShadow(shadow_rgbFace='#2C2C2C', alpha=0.4)])

        for ytick in self.ax.yaxis.get_major_ticks():
            ytick.label.set_fontproperties(self.fp)
            ytick.label.set_path_effects([patheffects.withSimplePatchShadow(shadow_rgbFace='#2C2C2C', alpha=0.4)])
