import os
import logging

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from handlers import handle_help, handle_start_game, handle_keyboard

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def main() -> None:
    updater = Updater(os.environ['BOT_TOKEN'])
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('help', handle_help))
    dispatcher.add_handler(CommandHandler('start_game_with', handle_start_game))
    dispatcher.add_handler(CallbackQueryHandler(handle_keyboard))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
