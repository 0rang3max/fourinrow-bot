from pymongo import MongoClient
import config
from game import Game
from exceptions import db_exceptions



client = MongoClient(
    f'mongodb+srv://{config.DB_USERNAME}:{config.DB_PASSWORD}'
    f'@{config.DB_HOST}/{config.DB_DATABASE}'
    '?retryWrites=true&w=majority'
)
db = getattr(client, config.DB_DATABASE)


class Games():
    table = db.games

    @classmethod
    def save_game(cls, game_id, game: Game) -> None:
        cls.table.update_one(
            {'gameId': game_id}, 
            {'$set': { k: v for k, v in game.serialize().items() if k != 'gameId'} },
            upsert=True
        )
    
    @classmethod
    def get_game(cls, game_id) -> Game:
        if game_data := cls.table.find_one({'gameId': game_id}):
            return Game.deserialize(game_data)
        raise db_exceptions.GameDoesNotExist

    @classmethod
    def delete_game(cls, game_id) -> None:
        cls.table.delete_one({'gameId': game_id})
