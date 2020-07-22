import logging

from matplotlib import patheffects
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from graphing.graph_objects.linegraph import LineGraph
from .datas import GRAPH_OPTIONS, user_selection, iso_codes, trend_buttons, trend_to_human_readable
from ..load_data import DataHandler
from helpers.msg_deletor import del_msg


def chosen_trend(update: Update, context: CallbackContext) -> GRAPH_OPTIONS:
    chosen = update.callback_query.data
    user_selection['trend'] = chosen

    logging.info(msg=f"trend is {chosen}")
    logging.info(msg=f"{user_selection}")

    country_data = DataHandler(iso=user_selection['country'])

    if 'case' in chosen:
        context.user_data['trend_data'] = country_data.case_data(_type=user_selection['trend'])
    else:
        context.user_data['trend_data'] = country_data.death_data(_type=user_selection['trend'])

    if user_selection['country'] == "OWID_WRL":
        context.user_data['covid_country'] = "The World"
    else:
        context.user_data['covid_country'] = iso_codes[user_selection['country']]

    # if 'covid_trend_pic' in context.user_data:
    #     del context.user_data['covid_trend_pic']

    if 'covid_trend_pic' not in context.user_data:
        context.user_data['covid_trend_pic'] = f"{update.effective_user.full_name}'s_trend"

    context.dispatcher.persistence.flush()

    send_graph(update, context, context.user_data['trend_data'][0], context.user_data['trend_data'][1],
               context.user_data['covid_country'])

    return GRAPH_OPTIONS


def send_graph(update, context, x, y, country, log=False):
    chat_id = update.effective_chat.id
    pic = context.user_data['covid_trend_pic']

    context.bot.send_chat_action(chat_id=chat_id, action='upload_photo')

    make_graph(LineGraph(x=x, y=y, logscale=log), country=country,
               trend_type=trend_to_human_readable(user_selection['trend']), save_loc=f"graphing/{pic}.png")

    del_msg(update, context)

    context.bot.send_photo(chat_id=chat_id, message_id=update.effective_message.message_id,
                           photo=open(f"graphing/{pic}.png", "rb"), reply_markup=InlineKeyboardMarkup(trend_buttons))


def make_graph(graph: LineGraph, country: str, trend_type: str, save_loc: str) -> None:
    graph.plot(line_color="#EBEE67", line_width=3, marker='o', markersize=7, markevery=slice(0, None, 8),
               markerfacecolor='#E9FB2A', solid_capstyle='round',
               path_effects=[patheffects.SimpleLineShadow(shadow_color='#331C7C', alpha=0.8), patheffects.Normal()])

    graph.enable_grid(axis='y')
    graph.set_fig_color(color='#51049E')
    graph.spine_config(spine_color="#E7F3F3", visibility=0.0, line_width=0.0)
    graph.axis_locator_formatter()
    graph.add_annotation()
    graph.tick_config()
    graph.set_title(country=country, _type=trend_type)
    # graph.show_graph()
    graph.save_graph(save_loc, color="#51049E")


def toggle_log(update: Update, context: CallbackContext) -> None:
    if 'log' not in context.user_data:
        context.user_data['log'] = False

    if not context.user_data['log']:
        context.user_data['log'] = True
        log = True
    else:
        context.user_data['log'] = False
        log = False

    send_graph(update, context, context.user_data['trend_data'][0], context.user_data['trend_data'][1],
               context.user_data['covid_country'], log=log)
