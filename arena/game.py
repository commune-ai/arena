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
                 password=None):

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
        self.account = Account(user=user, password=password)
        self.params = params
        self.max_time = max_time
        self.description = description
        self.epoch = epoch
        self.leaderboard_path = leaderboard_path
    init_game = __init__
    def start_game(self):
        game = {
            'params': self.params, 
            'time': c.time(),
        }
        game['tickets']  = {'owner': self.account.ticket(game)}

        return game
    


    
    def refresh(self):
        return [self.rm(path) for path in self.global_history_paths()]

    def metadata(self):
        return {
            'params': self.params(),
            'description': self.description
        }

    def create_game_path(self, game):
        path = self.leaderboard_path + '/' +  game['tickets']['user']['address'] + '/' + str(game['time']) + '.json'
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
    
    
    def submit_game(self, game):
        game = game or self.start_game()
        current_max_time = c.time() - game['time']
        assert current_max_time < self.max_time, 'Game expired'
        game_data = game.copy()
        tickets = game_data.pop('tickets')
        # veruft the user and owner signatures

        assert c.verify(game_data, signature=tickets['user']['signature'], address=tickets['user']['address']), str(game_data)
        # game_data.pop('output', None)

        # # verify the owner signature
        # assert c.verify(game_data, **tickets['owner'])

        # add the score to the game
        game['score'] = self.score(game)
        game_period = c.time() - game['time']
        assert game_period < self.max_time, 'Game expired'

        new_owner_ticket = self.account.ticket(game)
        game['tickets']['owner'] = new_owner_ticket
        # create a ticket 
        path = self.create_game_path(game)
        self.put_json(path, game)
        return game
        
    def score(self,  game):
        params = game['params']
        return abs((params['x'] + params['y']) - game['output'])
        
    def play_game(self, game):
        params = game['params']
        game['output'] =   params['x'] + params['y'] + 1
        return game
    forward = play_game
    
    def test(self, n=10):
        return self.play_n(n)
    
    def play(self, user='fam', password='fam', game=None):
        # start the game
        game = self.start_game()
        game = self.play_game(game)
        player = Account(user=user, password=password)
        
        game['tickets']['user'] =  player.ticket(game)
       
        return self.submit_game(game)
    
    def play_n(self, n=1, password='fam'):
        games = []
        for i in range(n):
            key_password = password + str(i)
            games += [self.play(key_password)]
        return games