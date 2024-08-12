
import arena as a
import commune as c

class DontSayIt(a.Game):
    forbidden_words = [
        'fuck',
        'shit', 
        'damnit'
    ]

    def __init__(self, 
                 forbidden_words = forbidden_words, 
                 model='model.openrouter'):
        self.params = {'forbidden_words': forbidden_words, 'model': model}
        self.init_game(params=self.params)

    def forward(self, game):
        return game['params']['forbidden_words']

    def score(self, game):
        text = game['text']
        forbidden_words = params['forbidden_words']
        return 1

  
    # def score(self, game) -> float:
    #     game['params']['text']
    #     for word in self.forbidden_words:
    #         if word in text:
    #             return 1
    #     return 0
    






        