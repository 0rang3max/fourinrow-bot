import config
import shelve
from game import Game
from exceptions import db_exceptions


class Games():
    @classmethod
    def save_game(cls, game_id: str, game: Game) -> None:
        with shelve.open(config.SHELVE_DB) as games:
            games[game_id] = game.serialize()
    
    @classmethod
    def get_game(cls, game_id: str) -> Game:
        with shelve.open(config.SHELVE_DB) as games:
            if not game_id in games:
                raise db_exceptions.GameDoesNotExist
            return Game.deserialize(games[game_id])

    @classmethod
    def delete_game(cls, game_id: str) -> None:
        with shelve.open(config.SHELVE_DB) as games:
            try:
                del games[game_id]
            except KeyError:
                raise db_exceptions.GameDoesNotExist
