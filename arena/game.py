import commune as c
import json
import numpy as np

class Game(c.Module):

    description = "add two numbers template game"
    
    def __init__(self, x=1, y=1):
        self.x = x
        self.y = y

    def play(self, output, ticket=None):
        score =  self.score(output)
        result = {
            'score': score
        }
        if ticket != None:
            assert c.verify(ticket)
            result['address'] = ticket['address']
            result['timestamp'] = ticket['data']['timestamp']
            self.save_result(result)

    def score(self, output):
        return abs((self.x + self.y) - output)

    def save_result(self, result):
        address = result['address']
        timestamp = result['timestamp']
        path =  f'history/{address}/{timestamp}.json'
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
            'params': self.params(),
            'description': self.description
        }