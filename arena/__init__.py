from .game import Game
from .account import Account
import commune as c
import os

class Arena(c.Module):
    game_directory= os.path.dirname(__file__) +  '/games'

    def game_paths(self, game_directory=None):
        game_directory = game_directory or self.game_directory
        paths = self.ls(game_directory)
        paths = list(filter(self.is_path_game, paths))
        return paths
    
    def get_name_from_path(self, path):
        path = path.split('/')[-1]
        if path.endswith('.py'):
            path = path[:-3]
        return path
    
    def name2path(self):
        names = self.game_names()
        paths = self.game_paths()
        name2path = dict(zip(names, paths))
        return name2path
    
    def name2objectpath(self):
        names = self.game_names()
        paths = self.game_paths()
        name2path = dict(zip(names, paths))
        name2objectpath = {name: 'arena.games.'+path.replace(self.game_directory + '/', '').replace('.py', '') for name, path in name2path.items()}
        return name2objectpath
    
    def game_names(self, game_directory=None):
        game_paths = self.game_paths(game_directory=game_directory)
        game_names = list(map(self.get_name_from_path, game_paths))
        return game_names
    
    def games(self):
        return self.game_names()
    
    def is_path_game(self, path, filename_options=['game.py']):
        '''
        two options of games, each contain a python file that is a class

        Game Python File
            - a class with a score and forward function
            - inherit from Game
            - the class needs to initialize the 



        Game Structure Modes
            file: 
                - needs to be a python file with a game name and a game function
            directory:
                - needs to have a game.py file
                - the file is the same name as the directory
        
        
        '''
        is_dir = self.isdir(path)
        if is_dir:
            filename_options += [path.split('/')[-1] + '.py']
        for filename in filename_options:

            

            if is_dir:
                game_path = path + '/' + filename
            else:
                game_path = path
            if self.exists(game_path):
                return True

        return False
    
    def get_game(self, name):
        path = self.name2objectpath()[name]
        return c.module(path)()
    

    def play(self, game='dontsayit', **kwargs):
        game =  self.get_game(game)
        return game.play(**kwargs)
    

    def primitives(self):
        return [Account, Game]
    
    def test(self, game='dontsayit', **kwargs):
        import arena as a
        results = {}
        for primitive in self.primitives():
            primitive = primitive()
            results[primitive.__class__.__name__] = primitive.test()
        return results


