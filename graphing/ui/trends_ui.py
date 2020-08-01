import logging
from datetime import timedelta

from matplotlib import patheffects
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from graphing.graph_objects.plotter import Plotter
from helpers.msg_deletor import del_msg
from .datas import GRAPH_OPTIONS, user_selection, iso_codes, trend_buttons, TREND_SELECTOR
from .utility import trend_to_human_readable, rolling_avg
from ..load_data import DataHandler

ROLLING_AVG = "rolling_avg"
REGULAR = "regular"


def chosen_trend(update: Update, context: CallbackContext) -> GRAPH_OPTIONS:
    chosen = update.callback_query.data
    user_selection['trend'] = chosen

    logging.info(msg=f"trend is {chosen=}")
    logging.info(msg=f"{user_selection=}")

    country_data = DataHandler(iso=user_selection['country'])

    # Assign trend data to user data memory-
    if 'case' in chosen:
        context.user_data['trend_data'] = country_data.case_data(_type=user_selection['trend'])

    elif any(obj in chosen for obj in {'test', 'rate'}):
        if user_selection['country'] == "OWID_WRL":
            update.callback_query.answer(text=f"{trend_to_human_readable(chosen).capitalize()} is only available "
                                              f"for individual countries!")
            return TREND_SELECTOR

        if "test" in chosen:
            chosen_data = country_data.tests_data(_type=user_selection['trend'], with_dates=True)
        else:
            chosen_data = country_data.pct_positive()

        if not chosen_data:
            update.callback_query.answer(text="Test data for this country is unavailable!")
            return TREND_SELECTOR

        context.user_data['trend_data'] = chosen_data
    else:
        context.user_data['trend_data'] = country_data.death_data(_type=user_selection['trend'])

    # Assign countries(iso code) to user data memory
    if user_selection['country'] == "OWID_WRL":
        context.user_data['covid_country'] = "The World"
    else:
        context.user_data['covid_country'] = iso_codes[user_selection['country']]

    if 'covid_trend_pic' not in context.user_data:
        context.user_data['covid_trend_pic'] = f"{update.effective_user.full_name}'s_trend"

    context.dispatcher.persistence.flush()  # Force save

    moving_avg, is_bar, y_data, is_pct = None, None, context.user_data['trend_data'][1], False

    # Make graph with bars if trend type selected was new cases/deaths or normal-
    if any(obj in chosen for obj in {'new', 'rate'}):
        moving_avg = rolling_avg(y_data, 7)
        is_bar = True
        is_pct = True if "rate" in chosen else False

    send_graph(update, context, x=context.user_data['trend_data'][0], y=y_data,
               country=context.user_data['covid_country'], moving_avg=moving_avg, is_bar=is_bar, is_pct=is_pct)

    return GRAPH_OPTIONS


def send_graph(update: Update, context: CallbackContext, x: list, y: list, country: str, log: bool = False,
               moving_avg: list = None, is_bar: bool = False, is_pct: bool = False) -> None:
    chat_id = update.effective_chat.id
    pic = context.user_data['covid_trend_pic']

    context.bot.send_chat_action(chat_id=chat_id, action='upload_photo')

    make_graph(graph=Plotter(x=x, y=y, logscale=log), country=country,
               trend_type=trend_to_human_readable(user_selection['trend']), save_loc=f"graphing/{pic}.png",
               rolling_data=moving_avg, is_bar=is_bar, is_pct=is_pct)

    del_msg(update, context)

    img_caption = ""

    if 'test' in user_selection['trend']:
        img_caption = "Test data can be missing for days for few countries\. Expect some discrepancies in " \
                      "the graph\.\n\n"

    elif 'rate' in user_selection['trend']:
        img_caption = "Calculated by dividing the new cases by the new tests done at that day\.\nTest data can be " \
                      "missing for days for few countries\. Expect some discrepancies in " \
                      "the graph\.\n\n"

    img_caption += f"_Data last fetched on: " \
                   f"{(context.bot_data['last_data_dl_date'] - timedelta(hours=4)).strftime('%B %d, %Y at %H:%M:%S')}" \
                   f" UTC_"

    context.bot.send_photo(chat_id=chat_id, message_id=update.effective_message.message_id,
                           photo=open(f"graphing/{pic}.png", "rb"), reply_markup=InlineKeyboardMarkup(trend_buttons),
                           caption=img_caption, parse_mode="MarkdownV2")


def make_graph(country: str, trend_type: str, save_loc: str, graph: Plotter, rolling_data: list = None,
               is_bar: bool = False, is_pct: bool = False) -> None:
    if is_bar and rolling_data:
        line_type = ROLLING_AVG
    else:
        line_type = REGULAR

    if is_bar:
        graph.bar_plot(capstyle='round', line_width=1, joinstyle='round', edgecolor="#05D36D", alpha=1,
                       path_effects=[patheffects.withSimplePatchShadow(shadow_rgbFace='#331C7C', alpha=0.8)],
                       bar_color="#05D36D", label=trend_type.capitalize())

    if line_type == ROLLING_AVG:
        graph.line_plot(line_color="#EBEE67", line_width=3.5, markerfacecolor='#E9FB2A', solid_capstyle='round',
                        moving_avg=rolling_data,
                        path_effects=[patheffects.SimpleLineShadow(shadow_color='#331C7C', alpha=0.6),
                                      patheffects.Normal()], label="7 day rolling average")
        graph.enable_legend()

    elif line_type == REGULAR:
        graph.line_plot(line_color="#EBEE67", line_width=3, marker='o', markersize=7, markevery=slice(0, None, 8),
                        markerfacecolor='#E9FB2A', solid_capstyle='round',
                        path_effects=[patheffects.SimpleLineShadow(shadow_color='#331C7C', alpha=0.8),
                                      patheffects.Normal()])

    graph.enable_grid(axis='y')
    graph.set_fig_color(color='#51049E')
    graph.spine_config(spine_color="#E7F3F3", visibility=0.0, line_width=0.0)

    if is_pct:
        graph.axis_locator_formatter(unit="%")
    else:
        graph.axis_locator_formatter()

    graph.add_annotation(is_pct=is_pct)
    graph.tick_config()
    graph.set_title(country=country, _type=trend_type)
    # graph.show_graph()
    graph.save_graph(save_loc, color="#51049E")


def toggle_log(update: Update, context: CallbackContext) -> GRAPH_OPTIONS:
    if 'log' not in context.user_data:
        context.user_data['log'] = False

    # Don't show logarithmic scales for new cases/deaths-
    if any(obj in user_selection['trend'] for obj in {'new', 'rate'}):
        update.callback_query.answer(text="Logarithmic scale for this type of graph is not suitable!")
        return GRAPH_OPTIONS

    # Check log state and reassign to 'toggle'-
    if not context.user_data['log']:
        context.user_data['log'] = True
        trend_buttons[0][-1].text = "Log scale ✅"
    else:
        context.user_data['log'] = False
        trend_buttons[0][-1].text = "Log scale ❌"

    context.dispatcher.persistence.flush()  # Force save

    send_graph(update, context, context.user_data['trend_data'][0], context.user_data['trend_data'][1],
               context.user_data['covid_country'], log=context.user_data['log'])

    return GRAPH_OPTIONS
