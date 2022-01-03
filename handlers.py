import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

import game_exceptions
from game import Game


GAMES = {}


def handle_help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('To start the game simply write `/start_game_with @username`')


def handle_start_game(update: Update, context: CallbackContext) -> None: 
    first_palayer = update.message.from_user.username
    user_regex = re.compile(r'\@([A-Za-z0-9_]*)')
    if not ( possible_users := user_regex.findall(update.message.text)):
        update.message.reply_text('You should mention a user!')
        return

    second_player = possible_users[-1] 
    bot_username = context.bot.get_me().username
    if second_player == bot_username:
        update.message.reply_text('You should mention a user (not a bot)!')
        return

    game = Game(players=[first_palayer, second_player])
    game_board_message = update.message.reply_text(f'{str(game)}')
    game_board_message_id = game_board_message.message_id
    GAMES[game_board_message_id] = game
    reply_markup = InlineKeyboardMarkup([
        [
        InlineKeyboardButton(
            str(num+1), callback_data=f'{game_board_message_id}_{str(num)}'
        ) for num in range(0, game.game_board.columns)
        ],
        [InlineKeyboardButton('I give up! 🥲', callback_data=f'{game_board_message_id}_surrender')]
    ])
    update.message.reply_text(f'@{first_palayer} vs @{second_player}', reply_markup=reply_markup)


def handle_keyboard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    game_id_str, players_move_str = query.data.split('_')
    game_id = int(game_id_str)
    game: Game = GAMES.get(game_id)
    if not game:
        query.answer('Game doesn`t exist anymore')
        return
    
    username = query.from_user.username
    game.check_players_move_order(username)
    if players_move_str == 'surrender':
        winner = (set(game.players.values()) - {username}).pop()
        context.bot.edit_message_text(
            chat_id=query.message.chat_id, message_id=game_id,
            text=f'{str(game)}\n@{username} gave up! @{winner} wins!'
        )
        del GAMES[game_id]
        return
    
    players_move = int(players_move_str)
    try: 
        is_winning_move = game.make_move(username, players_move)
    
    except game_exceptions.WrongPlayerMoveError:
        query.answer('It is not your move!')
        return

    except game_exceptions.ColumnIsFullError:
        query.answer('This column is full, chose another one!')
        return

    query.answer()
    if is_winning_move:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id, message_id=game_id,
            text=f'{str(game)}\nPlayer @{username} won!'
        )
        del GAMES[game_id]
        return

    if not game.game_board.moves_left:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id, message_id=game_id,
            text=f'{str(game)}\nNo more moves left. It\'s a draw!'
        )
        del GAMES[game_id]
        return

    context.bot.edit_message_text(
        chat_id=query.message.chat_id, message_id=game_id,
        text=str(game)
    )
