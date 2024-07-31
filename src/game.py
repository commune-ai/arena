import commune as c
from .account import Account

class Game(c.Module):

    def __init__(self, 
                 data  = {'x': 1, 'y': 2},
                 description = "add two numbers template game",
                 period = 10,
                 epoch = 10000,
                 password=None):

        """
        params:
            data: dict
                data to be used in the game
            description: str
                description of the game
            period: int
                time in seconds before the game expires
            password: str
                password to be used in creating the account
            epoch: int
                time in seconds before the leaderboard expires
            
        """
        
        
        self.account = Account(password= password or self.module_name())
        self.data = data
        self.period = period
        self.description = description
        self.epoch = epoch
        
    def game(self):
        import random
        game = {
            'data': {k: v + random.random() for k, v in self.data.items()}, 
            'time': c.time(),
        }
        game['users']  = {'owner': self.account.create_ticket(game)}

        return game
    
    def check_game_period(self, game):
        current_period = c.time() - game['time']
        assert current_period < self.period, 'Game expired'
        return {'msg': 'game is not stale'}
        
    
    def resolve_game(self, game=None):
        game = game or self.game()
        self.check_game_period(game)
        game_data = game.copy()
        game_data.pop('output')
        users = c.dict2munch(game_data.pop('users'))
        for user_names in users.keys():
            assert self.account.verify(game_data, signature=users[user_names]['signature'], address=users[user_names]['address'])
        game = c.dict2munch(game)
        assert game.output != None, 'Game output not set'
        return game
    

    def save_result(self, result):
        address = result['address']
        time = result['time']
        path =  f'history/{address}/{time}.json'
        self.put_json(path, result)

    def global_history_paths(self):
        return self.glob('history/**')
    
    def global_history(self):
        history = []
        for path in self.global_history_paths():
            history += [self.get_json(path)]
        return history
    
    def clear_history(self):
        return [self.rm(path) for path in self.global_history_paths()]

    def get_history(self, address=None, model=None):
        history_paths = self.get_history_paths(address=address, model=model)
        history = [self.get_json(fp) for fp in history_paths]
        return history
    
    def get_history_paths(self, address=None, model=None):
        address = address or self.key.ss58_address
        history_paths = []
        model_paths = [self.resolve_path(f'history/{model}')] if model else self.ls('history')
        for model_path in model_paths:
            user_folder = f'{model_path}/{address}'
            if not self.exists(user_folder):
                continue
            for fp in self.ls(user_folder):
                history_paths += [fp]
        return history_paths

    def metadata(self):
        return {
            'data': self.data(),
            'description': self.description
        }
    
    def play(self, password='fam', game=None, role='player'):
        player = Account(password=password)
        game = game or self.game()
        users = game.pop('users')
        users[role] = player.create_ticket(game)
        game['output'] = self.forward(game)
        game['users'] = users
        game = self.score_game(game)
        return c.munch2dict(game)
    
    def play_n(self, n=1, password='fam', role='player'):
        games = []
        for i in range(n):
            games += [self.play(password=password + str(i), role=role)]
        return games

    def create_game_path(self, game):
        path = self.resolve_path( 'leaderboard/'+ game['users']['player']['address'] + '/' + str(game['time']) + '.json')
        return path
    
    def path2time(self, path):
        return int(path.split('/')[-1].split('.')[0])
    
    def path2age(self, path):
        return c.time() - self.path2time(path)
    
    def path2address(self, path):
        return path.split('/')[-2]
    

    def leaderboard_directory(self):
        return self.resolve_path('leaderboard')
    
    
    def paths(self, clean_expired=True):
        paths =  self.glob(self.leaderboard_directory()+'/**')
        if clean_expired:
            for path in paths:
                expired = self.path2age(path) > self.epoch
                if expired:
                    self.rm(path)
                paths.remove(path)
                c.print(f'path: {path} expired: {expired} --> removing path')

        return paths

    def clear_leaderboard(self):
        return self.rm(self.leaderboard_directory())
    
    def leaderboard(self, columns = ['address', 'time', 'score', 'age']):
        leaderboard = []
        for path in self.paths():
            row = self.get_json(path)
            row['age'] = self.path2age(path)
            row['address'] = self.path2address(path)
            leaderboard += [row]
        df = c.df(leaderboard)
        if len(leaderboard) == 0:
            return leaderboard
        return df[columns]


    def score_game(self, game):
        game = self.resolve_game(game)
        game['score'] = self.score(game)
        path = self.create_game_path(game)
        self.put_json(path, game)
        
        return game
        
    def score(self,  game):
         return abs((game.data.x + game.data.y) - game.output)

        
    def forward(self, game):
        return  game['data']['x'] + game['data']['y'] + 1
    
