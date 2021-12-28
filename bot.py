import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import game_exceptions
from game import Game, GameBoard

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
TOKEN = '362895087:AAFiY6ja2NtNO3rtX25xi2oKMcgm2iqguNY'
GAMES = {}


def start_game(update: Update, context: CallbackContext) -> None:
    game_id = update.message.chat_id
    username = update.message.from_user.username
    if GAMES.get(game_id):
        update.message.reply_text('Game already started!')
        return
    GAMES[game_id] = Game(first_player=username)
    update.message.reply_text(f'@{username} started game! type /join to join.')


def end_game(update: Update, context: CallbackContext) -> None:
    game_id = update.message.chat_id
    
    if not (game := GAMES.get(game_id)):
        update.message.reply_text('No active games found!')
        return

    if update.message.from_user.username not in game.players.values():
        update.message.reply_text('Only players can stop the game!')
        return

    del GAMES[game_id]


def join(update: Update, context: CallbackContext) -> None:
    game_id = update.message.chat_id
    username = update.message.from_user.username
    game: Game = GAMES.get(game_id)
    if not game:
        update.message.reply_text('No active games found!')
        return
    try:
        game.add_player(username)
    except game_exceptions.SecondJoinAttemptError:
        update.message.reply_text(f'You can\'t play with yourself! Wait for other player!')
        return

    GAMES[game_id] = game
    update.message.reply_text(f'Game started!\n{str(game)}')


def make_move(update: Update, context: CallbackContext) -> None:
    game_id = update.message.chat_id
    username = update.message.from_user.username
    if not (game := GAMES.get(game_id)):
        update.message.reply_text('No active games found!')
        return
    if not game.players_ready:
        update.message.reply_text(game.not_ready_placeholder)
        return
    try:
        players_move = int(update.message.text.split(' ')[1])
    except ValueError:
        update.message.reply_text('Enter correct value, something like `/make_move 1`')
        return
    try: 
        is_winning_move = game.make_move(username, players_move)
    except game_exceptions.BadColumnChoiceError:
        update.message.reply_text('Choose column from 1 to 7')
    except game_exceptions.WrongPlayerMoveError:
        update.message.reply_text('It is not your move!')
    except game_exceptions.ColumnIsFullError:
        update.message.reply_text('This column is full, chose another one!')

    if is_winning_move:
        update.message.reply_text(f'Player @{username} won!')
        del GAMES[game_id]
        return

    if not game.game_board.moves_left:
        update.message.reply_text('No more moves left. It\'s a draw!')
        del GAMES[game_id]
        return

    update.message.reply_text(str(game))

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start_game', start_game))
    dispatcher.add_handler(CommandHandler('end_game', end_game))
    dispatcher.add_handler(CommandHandler('join', join))
    dispatcher.add_handler(CommandHandler('make_move', make_move))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
