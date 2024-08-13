import commune as c
from .account import Account


class Game(c.Module):


    """
    Steps
    
    """

    def __init__(self, 
                 params  = {'x': 1, 'y': 2, 'timeout': 10, 'fam': 'fam'},
                 description = "add two numbers template game",
                 max_time = 10,
                 epoch = 10000,
                 leaderboard_path = 'leaderboard', 
                 user=None,
                 password=None, **extra_params):
        """
        params:
            params: dict
                params to be used in the game, in this case x and y are the numbers to be added, and timeout is the time in seconds before the game expires
            description: str
                description of the game
            max_time: int
                time in seconds before the game expires
            password: str
                password to be used in creating the account
            epoch: int
                time in seconds before the leaderboard expires
            
        """
        self.max_time = max_time
        self.description = description 
        self.epoch = epoch
        self.leaderboard_path = leaderboard_path
        self.set_params(**params, **extra_params)
        self.login(user, password)
    init_game = __init__

    def login(self, user, password, role='owner'):
        self.account = Account(user=user, password=password, role='owner')
        return self.account

    def set_params(self, **params):
        self.params = params
        
    def game(self):
        game = self.params
        return game


    def start_game(self):
        game = {}
        game = c.copy(self.game())
        reserved_keys = ['signatures', 'timestamp', 'max_time', 'description', 'epoch']
        for key in reserved_keys:
            assert key not in game, f'key: {key} is reserved'
        # add game metadata
        game['description'] = self.description
        game['max_time'] = self.max_time
        game['epoch'] = self.epoch

        # have the owner signit to verify it is indeed the owner
        game = self.account.sign(game)
        return game
    


    
    def refresh(self):
        return self.rm(self.leaderboard_directory())

    def metadata(self):
        return {
            'params': self.params(),
            'description': self.description
        }

    def create_game_path(self, game):
        
        path = self.leaderboard_path + '/' +  game['signatures']['user']['address'] + '/' + str(game['timestamp']) + '.json'
        path = self.resolve_path(path)
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
    
    def leaderboard(self):
        leaderboard = []
        for path in self.paths():
            row = self.get_json(path)
            row['age'] = self.path2age(path)
            row['address'] = self.path2address(path)
            leaderboard += [row]
        df = c.df(leaderboard)
        if len(leaderboard) == 0:
            return leaderboard
        return df
    
    
    def submit_game(self, game):
        game = game or self.start_game()
        game_period = c.time() - game['timestamp']
        assert game_period < self.max_time, 'Game expired'
        assert game['signatures']['owner']['address'] == self.account.key.ss58_address
        assert self.account.verify(game), 'Ticket verification failed'
        # game_data.pop('output', None)

        # # verify the owner signature
        # assert c.verify(game_data, **signatures['owner'])

        # add the score to the game
        game['latency'] = game_period
        game['score'] = self.score(game)
        assert game_period < self.max_time, 'Game expired'

        game = self.account.sign(game)
        assert self.account.verify(game)
        # create a ticket 
        path = self.create_game_path(game)
        self.put_json(path, game)
        return game
        
    def score(self,  game):
        return abs((game['x'] + game['y']) - game['output'])
        
    def forward(self, game, **kwargs):
        game['output'] =  game['x'] + game['y']
        return game

    def test(self):
        return self.play()
    
    def play(self, user='fam', password='fam', **kwargs):
        user = Account(user=user, password=password, role='user')
        game = self.start_game()
        game.update(kwargs)
        game = self.forward(game)
        game =  user.sign(game)       
        game =  self.submit_game(game)
        game.pop('signatures', None)
        return game
    

