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

        case_no = str(int(self.y[-1])).__len__()

        if case_no >= 7:
            offset = 19
        elif 5 <= case_no:
            offset = 17
        else:
            offset = 11

        self.ax.text(x=annotation.xy[0] + offset, y=annotation.xy[-1], s=format(int(self.y[-1]), ',d'), ha='center',
                     fontfamily='Product Sans', color='#FFFFFF', fontsize=14, fontweight='bold', va='center',
                     path_effects=[patheffects.withSimplePatchShadow(shadow_rgbFace='#2C2C2C', alpha=0.2)],
                     clip_on=False)

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

# def plotter(data):
#     x = data[0]  # Dates
#     y = data[1]  # Total cases
#
#     canvas, ax = plt.subplots(1, 1, figsize=(10, 8))  # That fig size is perfect for 1920x1080 (Don't change this!)
#
#     ax.plot(x, y, marker='o', markersize=7, color='#EBEE67', linewidth=3, markevery=slice(0, None, 8),
#             markerfacecolor='#E9FB2A', solid_capstyle='round',
#             path_effects=[patheffects.SimpleLineShadow(shadow_color='#331C7C', alpha=0.8),
#                           patheffects.Normal()])  # Makes bar graph with shadows)
#
#     ax.grid(b=True, axis='y')  # Enable grid
#     ax.set_axisbelow(True)  # Makes grid lines go behind line
#     # limit = ax.set_ylim(top=plt.ylim()[-1] - 1000, bottom=-1000)  # Slightly cut off y-axis @ top, and adjust @ bottom
#     # print(limit)
#     ax.set_yscale(value='log')
#
#     canvas.patch.set_facecolor("#51049E")  # Set to purple
#     ax.patch.set_facecolor("#51049E")
#
#     # Remove the 'box' like look of graph-
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.spines['bottom'].set_linewidth(0.0)
#     ax.spines['left'].set_visible(0.0)
#
#     ax.spines['left'].set_color("#E7F3F3")
#     ax.spines['bottom'].set_color("#E7F3F3")
#
#     # Set date and a clever formatter-
#     locator = AutoDateLocator()
#     formatter = ConciseDateFormatter(locator)
#
#     # Convert cases numbers to human readable form- Eg: 7000 -> 7k
#     human_format = EngFormatter(unit='', sep="")
#
#     ax.xaxis.set_major_locator(locator)
#     ax.xaxis.set_major_formatter(formatter)
#
#     ax.yaxis.set_major_formatter(human_format)
#
#     # Put arrow head on last case
#     annotation = ax.annotate("", xy=(date2num(x[-1]) + 3, y[-1]), xytext=(1, 0), textcoords='offset points',
#                              arrowprops={'color': '#02D4F5', 'headwidth': 12}, annotation_clip=False, ha='center')
#     print(annotation.xy)
#
#     case_no = str(int(y[-1])).__len__()
#     if case_no >= 7:
#         offset = 16
#     elif 5 <= case_no:
#         offset = 13
#     else:
#         offset = 9
#
#     ax.text(x=annotation.xy[0] + offset, y=annotation.xy[-1], s=format(int(y[-1]), ',d'), ha='center',
#             fontfamily='Product Sans', color='#FFFFFF', fontsize=13, fontweight='semibold', va='center')
#
#     ax.set_title(label="TOTAL CASES\nUAE",
#                  fontdict={'fontname': 'Product Sans', 'size': 21, 'weight': 'semibold', 'color': '#EEEEEE'},
#                  loc='center', pad=6.0,
#                  path_effects=[patheffects.SimpleLineShadow(shadow_color='#331C7C', alpha=0.8), patheffects.Normal()],
#                  clip_on=False, wrap=True)
#
#     # Change tick properties such as tick markers, color, transparency, etc-
#     ax.tick_params(axis='x', grid_alpha=0.4, color='#FFFFFF', direction='inout', grid_color='#FFFFFF',
#                    grid_linewidth=0.0, labelcolor="#EBF7F7")
#     ax.tick_params(axis='y', colors='#FFFFFF', grid_alpha=0.5, grid_color='#F65BF1', left=False, direction='inout',
#                    grid_linewidth=0.3, labelcolor="#EBF7F7", which='both')
#
#     fp = FontProperties(family='Product Sans', variant='small-caps', stretch=460, weight='demibold', size=11)
#
#     for xtick in ax.xaxis.get_major_ticks():
#         xtick.label.set_fontproperties(fp)
#
#     for ytick in ax.yaxis.get_major_ticks():
#         ytick.label.set_fontproperties(fp)
#
#     plt.savefig("cases.png", facecolor="#51049E")  # Save figure with same 'purple' fig color
#
#     plt.show()


# def make_graph(graph: LineGraph):
#     graph.plot(line_color="#EBEE67", line_width=3, marker='o', markersize=7, markevery=slice(0, None, 8),
#                markerfacecolor='#E9FB2A', solid_capstyle='round',
#                path_effects=[patheffects.SimpleLineShadow(shadow_color='#331C7C', alpha=0.8), patheffects.Normal()])
#
#     graph.enable_grid(axis='y')
#     graph.set_fig_color(color='#51049E')
#     graph.spine_config(spine_color="#E7F3F3", visibility=0.0, line_width=0.0)
#     graph.axis_locator_formatter()
#     graph.add_annotation()
#     graph.tick_config()
#     graph.set_title(country='United States', _type='TOTAL DEATHS')
#     graph.show_graph()
#     graph.save_graph("../cases.png", color="#51049E")


# x, y = DataHandler(iso="USA").death_data()
# make_graph(LineGraph(x=x, y=y, logscale=False))
