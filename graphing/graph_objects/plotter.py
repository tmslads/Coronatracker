from matplotlib import patheffects
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter, date2num
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import EngFormatter

from ..graph_objects.basegraph import BaseGraph


# from ..load_data import DataHandler


class Plotter(BaseGraph):
    fp = FontProperties(family='Product Sans', variant='small-caps', stretch=460, weight='demibold', size=11)

    def __init__(self, x: list, y: list, logscale: bool = False):
        super().__init__()
        self.x = x
        self.y = y
        self.logscale = logscale

    def line_plot(self, line_color: str, line_width: int or float, moving_avg: list = False, **kwargs):
        if moving_avg:
            self.ax.plot(self.x, moving_avg, color=line_color, linewidth=line_width, **kwargs)
        else:
            self.ax.plot(self.x, self.y, color=line_color, linewidth=line_width, **kwargs)

        if self.logscale:
            self.ax.set_yscale(value='log')

            self.ax.set_ylabel(ylabel="LOG", y=0.9, ha='right', rotation='horizontal', labelpad=6,
                               bbox={'boxstyle': 'round', 'facecolor': '#FFDD47'}, fontproperties=self.fp)

    def bar_plot(self, bar_color: str, line_width: int, **kwargs):
        self.ax.bar(x=self.x, height=self.y, color=bar_color, linewidth=line_width, **kwargs)

    def axis_locator_formatter(self):
        # Set date and a clever formatter-
        locator = AutoDateLocator()
        formatter = ConciseDateFormatter(locator)

        # Convert cases numbers to human readable form- Eg: 7000 -> 7k
        human_format = EngFormatter(sep="")

        super().set_locator_formatter(x_locator=locator, x_formatter=formatter, y_formatter=human_format)

    def add_annotation(self):
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
            offset = 25

        self.ax.annotate(text=format(int(self.y[-1]), ',d'), ha='center', va='center', fontweight='bold',
                         xy=(annotation.xy[0], annotation.xy[-1]),
                         xytext=(offset, 0), textcoords="offset points",
                         path_effects=[patheffects.withSimplePatchShadow(shadow_rgbFace='#2C2C2C', alpha=0.2)],
                         clip_on=False, wrap=True, fontfamily='Product Sans', color='#FFFFFF', fontsize=14)

    def tick_config(self):
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
