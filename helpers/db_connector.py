# Helper function to connect to database and get result.
import sqlite3
from typing import Union, List, Tuple

from telegram import Update

from helpers.namer import get_chat_name


def connection(query: str,
               update: Update = None,
               fetchall: bool = False,
               table_update: bool = False) -> Union[List[Tuple[str]], str, None]:

    """
    Connects to a database and executes the given query.

    Args:
        query (:obj:`str`): The query to execute.
        update (:obj:`telegram.Update`, optional): Should be passed in whenever the query is directly related to the
            user. This is almost always passed in. Defaults to `None`.
        fetchall (:obj:'bool`, optional): Set to True if you want fetch all the results of your query.
            Defaults to `False`.
        table_update (:obj:'bool`, optional): Set to True if the query is performing a update table operation.
            Defaults to `False`.
    """

    conn = sqlite3.connect('./files/bot_settings.db')
    c = conn.cursor()

    if update is not None:
        chat_id = update.effective_chat.id
        c.execute(f"SELECT EXISTS(SELECT * FROM CHAT_SETTINGS WHERE chat_id = {chat_id});")
        result = c.fetchone()

        if not result[0]:  # If /alert was never called
            name = get_chat_name(update)

            c.execute(f"INSERT INTO CHAT_SETTINGS VALUES({chat_id},'{name}','❌');")  # First time use
            conn.commit()

    c.execute(query)

    if table_update:
        conn.commit()
        return

    if fetchall:
        result = c.fetchall()
    else:
        result = c.fetchone()
        result = result[0]

    conn.close()

    return result
