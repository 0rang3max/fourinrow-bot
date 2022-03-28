import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

import config
from exceptions import game_exceptions, db_exceptions
from game import Game


def _get_keyboard(game_board_message_id, game):
    return InlineKeyboardMarkup([
        [
        InlineKeyboardButton(
            str(num+1), callback_data=f'{game_board_message_id}_{str(num)}'
        ) for num in range(0, game.game_board.columns)
        ],
        [InlineKeyboardButton('I give up! 🥲', callback_data=f'{game_board_message_id}_surrender')]
    ])


def handle_help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('To start the game simply write `/start_game_with @username`')


def handle_start_game(update: Update, context: CallbackContext) -> None: 
    player = update.message.from_user.username
    bot = context.bot
    chat_id = update.message.chat_id
    msg = bot.send_message(chat_id, f'@{player} hosted a game!')
    bot.edit_message_reply_markup(
        chat_id,
        msg.message_id,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Join Game', callback_data=f'{msg.message_id}_start@{player}')]]
        )
    )

def handle_keyboard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    username = query.from_user.username
    game_id, players_move_str = query.data.split('_')

    if 'start' in players_move_str:
        first_player = players_move_str.split('@')[1]
        second_player = username
        if first_player == second_player and not config.TESTING:
            query.answer('You can`t play with yourself!')
            return

        game = Game(players=[username, players_move_str.split('@')[1]], game_id=game_id)
        game.save()
        context.bot.edit_message_text(
            chat_id=query.message.chat_id, message_id=game_id,
            text=f'{game.game_field_str}\n{game.current_move_str}',
            reply_markup=_get_keyboard(game_id, game)
        )
        return

    try:
        game: Game = Game.get_by_id(game_id)
    except db_exceptions.GameDoesNotExist:
        query.answer('Game doesn`t exist anymore')
        return

    game.check_players_move_order(username)
    if players_move_str == 'surrender':
        winner = (set(game.players.values()) - {username}).pop()
        context.bot.edit_message_text(
            chat_id=query.message.chat_id, message_id=game_id,
            text=f'{game.game_field_str}\n@{username} gave up! @{winner} wins!'
        )
        del game
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
            text=f'{game.game_field_str}\nPlayer @{username} won!'
        )
        del game
        return

    if not game.game_board.moves_left:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id, message_id=game_id,
            text=f'{game.game_field_str}\nNo more moves left. It\'s a draw!'
        )
        del game
        return
    
    game.save()
    context.bot.edit_message_text(
        chat_id=query.message.chat_id, message_id=game_id,
        text=f'{game.game_field_str}\n{game.current_move_str}',
        reply_markup=_get_keyboard(game_id, game)
    )
