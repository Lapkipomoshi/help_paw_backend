import sys
import traceback

import telebot
from django.utils.deprecation import MiddlewareMixin

from help_paw.settings import ALERT_TO, ALERT_TOKEN


class CatchErrorsMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        bot = telebot.TeleBot(ALERT_TOKEN)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stack = traceback.extract_tb(exc_traceback)
        string_to_unpack = stack.format()
        string_to_send = f'---------------Произошла ошибка {exception}---------------\n'
        for s in string_to_unpack:
            string_to_send = string_to_send + s + '\n'
        string_to_send += '---------------Конец трейса---------------'
        bot.send_message(ALERT_TO, string_to_send)
